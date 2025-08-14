import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.guardrail import Guardrail
import logging

logger = logging.getLogger(__name__)

class GuardrailService:
    def __init__(self):
        self.cache = {}
        
    async def load_guardrails(self, db: AsyncSession):
        """Load active guardrails from database"""
        result = await db.execute(
            select(Guardrail).where(Guardrail.is_active == True).order_by(Guardrail.priority)
        )
        guardrails = result.scalars().all()
        
        self.cache = {
            "regex": [],
            "keyword": [],
            "semantic": []
        }
        
        for guardrail in guardrails:
            self.cache[guardrail.rule_type].append({
                "id": str(guardrail.id),
                "name": guardrail.name,
                "pattern": guardrail.pattern,
                "action": guardrail.action,
                "severity": guardrail.severity,
                "message": guardrail.message,
                "metadata": guardrail.metadata
            })
    
    async def check_input(self, text: str, db: AsyncSession) -> Dict[str, Any]:
        """Check input text against all guardrails"""
        if not self.cache:
            await self.load_guardrails(db)
        
        violations = []
        actions_to_take = set()
        
        # Check regex rules
        for rule in self.cache.get("regex", []):
            if self._check_regex(text, rule["pattern"]):
                violations.append(rule)
                actions_to_take.add(rule["action"])
        
        # Check keyword rules
        for rule in self.cache.get("keyword", []):
            if self._check_keywords(text, rule["pattern"]):
                violations.append(rule)
                actions_to_take.add(rule["action"])
        
        # Determine final action
        if "block" in actions_to_take:
            action = "block"
        elif "transform" in actions_to_take:
            action = "transform"
        elif "warn" in actions_to_take:
            action = "warn"
        elif "flag" in actions_to_take:
            action = "flag"
        else:
            action = "allow"
        
        # Get highest severity
        severity = "none"
        if violations:
            severity_order = ["critical", "high", "medium", "low"]
            for sev in severity_order:
                if any(v["severity"] == sev for v in violations):
                    severity = sev
                    break
        
        result = {
            "action": action,
            "severity": severity,
            "violations": violations,
            "original_text": text
        }
        
        # Apply transformation if needed
        if action == "transform":
            result["transformed_text"] = self._apply_transformations(text, violations)
        
        # Generate warning message
        if action in ["warn", "block"]:
            result["message"] = self._generate_message(violations)
        
        return result
    
    async def check_output(self, text: str, db: AsyncSession) -> Dict[str, Any]:
        """Check output text before sending to user"""
        return await self.check_input(text, db)
    
    def _check_regex(self, text: str, pattern: str) -> bool:
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error as e:
            logger.error(f"Invalid regex pattern: {pattern}, error: {e}")
            return False
    
    def _check_keywords(self, text: str, keywords_str: str) -> bool:
        keywords = [k.strip().lower() for k in keywords_str.split(",")]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    def _apply_transformations(self, text: str, violations: List[Dict]) -> str:
        transformed = text
        
        for rule in violations:
            if rule["action"] != "transform":
                continue
            
            metadata = rule.get("metadata", {})
            replacement = metadata.get("replacement", "[REDACTED]")
            
            if rule.get("rule_type") == "regex":
                try:
                    transformed = re.sub(
                        rule["pattern"],
                        replacement,
                        transformed,
                        flags=re.IGNORECASE
                    )
                except re.error:
                    pass
            elif rule.get("rule_type") == "keyword":
                keywords = [k.strip() for k in rule["pattern"].split(",")]
                for keyword in keywords:
                    transformed = re.sub(
                        re.escape(keyword),
                        replacement,
                        transformed,
                        flags=re.IGNORECASE
                    )
        
        return transformed
    
    def _generate_message(self, violations: List[Dict]) -> str:
        if not violations:
            return ""
        
        # Use custom message from highest severity violation
        for violation in violations:
            if violation.get("message"):
                return violation["message"]
        
        # Default messages
        severities = [v["severity"] for v in violations]
        if "critical" in severities:
            return "This content violates critical security policies and cannot be processed."
        elif "high" in severities:
            return "This content contains sensitive information that requires careful handling."
        elif "medium" in severities:
            return "Please review your input for potentially sensitive content."
        else:
            return "Your input has been flagged for review."
    
    async def create_guardrail(
        self,
        db: AsyncSession,
        name: str,
        rule_type: str,
        pattern: str,
        action: str,
        severity: str = "low",
        message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Guardrail:
        guardrail = Guardrail(
            name=name,
            rule_type=rule_type,
            pattern=pattern,
            action=action,
            severity=severity,
            message=message,
            metadata=metadata or {}
        )
        
        db.add(guardrail)
        await db.commit()
        await db.refresh(guardrail)
        
        # Reload cache
        await self.load_guardrails(db)
        
        return guardrail

guardrail_service = GuardrailService()