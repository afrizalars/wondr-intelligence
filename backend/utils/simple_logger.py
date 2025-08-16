"""
Simple logging utilities for Wondr Intelligence backend.
Provides structured logging without external dependencies.
"""
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import json

class SimpleFormatter(logging.Formatter):
    """Custom formatter with structured output for better readability."""
    
    def format(self, record):
        # Format timestamp
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        
        # Extract component from logger name
        component = self._get_component(record.name)
        
        # Get the message
        message = record.getMessage()
        
        # Format with simple prefixes for different types
        if ">>>" in message:  # Input flow
            prefix = "→→→"
        elif "<<<" in message:  # Output flow
            prefix = "←←←"
        elif "===" in message:  # Section separator
            prefix = "═══"
        elif "⚡" in message:  # Performance metric
            prefix = "[PERF]"
        elif "✓" in message:  # Success
            prefix = "[OK]"
        elif "✗" in message:  # Failure
            prefix = "[FAIL]"
        else:
            prefix = f"[{component:^8}]"
        
        # Build formatted message
        formatted = f"{timestamp} {prefix} [{record.levelname:^7}] {message}"
        
        # Add extra data if present
        if hasattr(record, 'extra_data'):
            formatted += f"\n  └─ {json.dumps(record.extra_data, indent=2)}"
        
        return formatted
    
    def _get_component(self, logger_name: str) -> str:
        """Map logger name to component."""
        if 'routers' in logger_name:
            return 'API'
        elif 'brain' in logger_name:
            return 'BRAIN'
        elif 'agents' in logger_name:
            return 'AGENT'
        elif 'reasoning' in logger_name:
            return 'REASON'
        elif 'llm' in logger_name:
            return 'LLM'
        elif 'database' in logger_name or 'models' in logger_name:
            return 'DB'
        elif 'guardrail' in logger_name:
            return 'GUARD'
        else:
            return 'SYSTEM'


class FlowLogger:
    """Helper class for logging query processing flow."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.request_id = None
        self.start_time = None
    
    def start_request(self, request_id: str, query: str, cif: str):
        """Log the start of a new request."""
        self.request_id = request_id
        self.start_time = datetime.now()
        self.logger.info("=" * 60)
        self.logger.info(f">>> NEW REQUEST: {request_id[:8]}")
        self.logger.info(f">>> Query: '{query}'")
        self.logger.info(f">>> CIF: {cif}")
        self.logger.info("=" * 60)
    
    def log_step(self, step: str, details: Optional[Dict[str, Any]] = None):
        """Log a step in the processing flow."""
        message = f"[{self.request_id[:8]}] {step}"
        if details:
            self.logger.info(message, extra={'extra_data': details})
        else:
            self.logger.info(message)
    
    def log_agent_activation(self, agent_name: str, context: Dict[str, Any]):
        """Log agent activation."""
        self.logger.info(f"⚡ Activating {agent_name}")
        if context:
            relevant_context = {k: v for k, v in context.items() if v}
            if relevant_context:
                self.logger.debug(f"  Context: {relevant_context}")
    
    def log_agent_result(self, agent_name: str, execution_time_ms: int, result_count: int = 0):
        """Log agent completion."""
        if result_count > 0:
            self.logger.info(f"✓ {agent_name} completed in {execution_time_ms}ms - Found {result_count} results")
        else:
            self.logger.info(f"✓ {agent_name} completed in {execution_time_ms}ms")
    
    def log_agent_error(self, agent_name: str, error: str):
        """Log agent error."""
        self.logger.error(f"✗ {agent_name} failed: {error}")
    
    def log_reasoning(self, response_type: str, data_sources: int):
        """Log reasoning synthesis."""
        self.logger.info(f">>> Reasoning: {response_type} from {data_sources} sources")
    
    def log_llm_call(self, model: str, tokens: int = None):
        """Log LLM processing."""
        if tokens:
            self.logger.info(f">>> LLM: Generating response with {model} ({tokens} tokens)")
        else:
            self.logger.info(f">>> LLM: Generating response with {model}")
    
    def end_request(self, status: str = "SUCCESS", total_time_ms: int = None):
        """Log the end of a request."""
        if not total_time_ms and self.start_time:
            total_time_ms = int((datetime.now() - self.start_time).total_seconds() * 1000)
        
        self.logger.info("=" * 60)
        if status == "SUCCESS":
            self.logger.info(f"<<< RESPONSE READY: {self.request_id[:8]}")
            self.logger.info(f"⚡ Total time: {total_time_ms}ms")
        else:
            self.logger.error(f"<<< REQUEST FAILED: {self.request_id[:8]}")
            self.logger.error(f"⚡ Failed after: {total_time_ms}ms")
        self.logger.info("=" * 60)
        self.logger.info("")  # Empty line for readability


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup a logger with simple formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with simple formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(SimpleFormatter())
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_flow_logger(name: str) -> FlowLogger:
    """Get a flow logger instance."""
    logger = setup_logger(name)
    return FlowLogger(logger)