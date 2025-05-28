from typing import Dict, Any, List, Optional
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.llms import Ollama
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from research_assistant.llm.ollama_client import OllamaClient
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class LangChainManager:
    """Manager for LangChain workflows."""

    def __init__(
        self,
        model_name: str = "mistral",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7
    ):
        """
        Initialize the LangChain manager.

        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for the Ollama API
            temperature: Sampling temperature for text generation
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.llm = Ollama(
            model=model_name,
            base_url=base_url,
            temperature=temperature
        )
        self.embeddings = OllamaEmbeddings(
            model=model_name,
            base_url=base_url
        )
        self.memory = ConversationBufferMemory()
        self.logger = get_logger(f"langchain.{model_name}")

    def create_summarization_chain(self) -> LLMChain:
        """
        Create a chain for content summarization.

        Returns:
            LLMChain for summarization
        """
        template = """Please provide a concise summary of the following content:

Content:
{content}

Focus on the key points and main ideas. The summary should be clear and informative.

Summary:"""

        prompt = PromptTemplate(
            input_variables=["content"],
            template=template
        )

        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True
        )

    def create_analysis_chain(self) -> LLMChain:
        """
        Create a chain for content analysis.

        Returns:
            LLMChain for analysis
        """
        template = """Analyze the following content and provide insights:

Content:
{content}

Please provide:
1. Key findings
2. Important implications
3. Potential areas for further research

Analysis:"""

        prompt = PromptTemplate(
            input_variables=["content"],
            template=template
        )

        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True
        )

    def create_research_chain(self) -> SimpleSequentialChain:
        """
        Create a chain for research analysis.

        Returns:
            SimpleSequentialChain for research
        """
        # First chain: Summarize content
        summarize_template = """Summarize the following research content:

Content:
{content}

Summary:"""

        summarize_prompt = PromptTemplate(
            input_variables=["content"],
            template=summarize_template
        )

        summarize_chain = LLMChain(
            llm=self.llm,
            prompt=summarize_prompt,
            verbose=True
        )

        # Second chain: Analyze summary
        analyze_template = """Based on the following summary, provide a detailed analysis:

Summary:
{summary}

Please include:
1. Key findings
2. Methodology assessment
3. Limitations
4. Future implications

Analysis:"""

        analyze_prompt = PromptTemplate(
            input_variables=["summary"],
            template=analyze_template
        )

        analyze_chain = LLMChain(
            llm=self.llm,
            prompt=analyze_prompt,
            verbose=True
        )

        # Combine chains
        return SimpleSequentialChain(
            chains=[summarize_chain, analyze_chain],
            verbose=True
        )

    def create_vector_store(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Chroma:
        """
        Create a vector store from texts.

        Args:
            texts: List of texts to store
            metadatas: Optional list of metadata dictionaries

        Returns:
            Chroma vector store
        """
        # Split texts
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        documents = text_splitter.create_documents(texts, metadatas=metadatas)

        # Create vector store
        return Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings
        )

    async def close(self):
        """Close the LangChain manager."""
        try:
            if hasattr(self.llm, 'close'):
                await self.llm.close()
        except Exception as e:
            self.logger.error(f"Error closing LangChain manager: {str(e)}") 