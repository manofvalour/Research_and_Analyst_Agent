import uuid
import os
from fastapi.responses import FileResponse
from research_and_analyst.utils.model_loader import ModelLoader
from research_and_analyst.workflows.report_generator_workflow import AutonomousReportGenerator
from research_and_analyst.logger import GLOBAL_LOGGER
from research_and_analyst.exceptions.custom_exception import ResearchAnalystException
from langgraph.checkpoint.memory import MemorySaver

_shared_memory = MemorySaver()

class ReportService:
    def __init__(self):
        self.llm = ModelLoader().load_llm()
        self.reporter = AutonomousReportGenerator(self.llm)
        self.reporter.memory = _shared_memory
        self.graph = self.reporter.build_graph()
        self.logger= GLOBAL_LOGGER.bind(module="ReportService")

    def start_report_generation(self, topic: str, max_analysts: int):
        """Trigger the autonomous report pipeline."""

        try:
            thread_id = str(uuid.uuid4())
            thread = {"Configurable": {'thread_id': thread_id}}
            self.logger.info('Starting report pipeline', topic=topic, thread_id=thread_id)

            for _ in self.graph.stream({'topic': topic, 'max_analysts': max_analysts}, thread,stream_mode='values'):
                pass
            return  {'thread_id': thread_id, 'message': "Pipeine initiated successfully"}
        
        except Exception as e:
            self.logger.error("Error initializing report generation", eror=str(e))
            raise ResearchAnalystException('failed to start report generation', e)
        
    
    def submit_feedback(self, thread_id:str, feedback:str):
        pass

    def get_report_state(self, thread_id:str):
        pass

    @staticmethod
    def download_file(file_name: str):
        """ Download generated report"""
        report_dir = os.path.oin(os.getcwd(), 'generated_report')
        for root, _, files in os.walk(report_dir):
            if file_name in files:
                return FileResponse(
                    path= os.path.join(root, file_name),
                    filename = file_name,
                    media_type = "application/octet-stream"
                )
            
            return {'error': f"file{file_name} not found"}
