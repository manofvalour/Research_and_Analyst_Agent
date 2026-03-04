
class AutonomousReportGenerator:
    def __init__(self):
        pass

    def _save_as_pdf(self,text:str, file_path:str):
        try:
            pass
        except Exception as e:
            self.logger.error("PDF save failed", path=file_path, error=str(e))
            riae ResearchAnalystException("Error saving PDF report", e)
    def build_graph(self):
        """ Construct the report generation graph"""
        try:
            self.logger.info("Building report generation graph")
            builder = StateGraph(ResearchGraphState)
            interview_graph = InterviewGraphBuilder(self.llm, self.tavily_search).build()

            def initiate_all_interview(state: ResearhGraphState):
                topic = state.get('topic', 'Untitled Topic')
                analysts = state.get('analysts', [])
                if not analysts:
                    self.logger.warning("No analysts found - skipping interviews")
                    return END
                return[
                    Send(
                        "conduct_interview",
                        {
                            'analyst': analyst,
                            'messages': [HumanMessage(content=f"So, Let's discuss about {topic}.")],
                            "max_num_of_turns":2,
                            "context": [],
                            "interview": "",
                            "sections": [],
                        },
                    )
                    for analyst in analysts
                ]
            
            builder.add_node("Create_analyst", self.create_analyst)
            builder.add_node('Human_feedback', self.human_feedback)
            builder.add_node("conduct_interview", interview_graph)
            builder.add_node("write_report", self.write_report)
            builder.add_node("write_introduction", self.write_introduction)
            builder.add_node('write_conclusion', self.write_conclusion)
            builder.add_node("finalize_report", self.finalize_report)

            builder.add_edge(START, 'create_analyst')
            builder.add_edge("create_analyst", "human_feedback")
            builder.add_conditional_edges(
                "human_feedback",
                initiate_all_interview,
                ['conduct_interview', END]
            )
            builder.add_edge('conduct_interview', 'write_report')
            builder.add_edge('conduct_interview','write_introduction')
            builder.add_edge('conduct_interview', "write_conclusion")
            builder.add_edge(['write_report', 'write_introduction', 'write_conclusion'], "finalize_report")
            builder.add_edge("finalize_report", END)

            graph = builder.compile(interupt_before=['human_feedback'], checkpointer= self.memory)
            self.logger.info("Report geneation graph built successfully")
