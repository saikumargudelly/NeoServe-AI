from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the NeoServe AI system.
    """
    
    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name of the agent
            config: Optional configuration dictionary
        """
        self.agent_name = agent_name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.initialize_agent()
    
    def initialize_agent(self) -> None:
        """
        Initialize agent-specific resources.
        Override in child classes if needed.
        """
        pass
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return a response.
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            Dictionary containing the agent's response
        """
        pass
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate the input data before processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            bool: True if input is valid, False otherwise
        """
        required_fields = self.config.get("required_fields", [])
        for field in required_fields:
            if field not in input_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main processing logic with input validation.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Dictionary containing the agent's response
        """
        try:
            if not await self.validate_input(input_data):
                return {
                    "status": "error",
                    "message": "Invalid input data",
                    "agent": self.agent_name
                }
            
            result = await self.process(input_data)
            return {
                "status": "success",
                "agent": self.agent_name,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error in {self.agent_name}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "agent": self.agent_name,
                "message": str(e)
            }
