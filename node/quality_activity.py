from . import quality_node

class QualityActivity(quality_node.QualityNode):
    def __init__(self, nid, pid, parents, children, type, subtype, task, achievement, contribution, is_manual):
        super().__init__(nid, pid, parents, children, type, subtype, task, achievement, contribution)
        self.is_manual = is_manual

    #デバック用
    def __str__(self):
        return f'QualityActivity(nid={self.nid}, type={self.type})'
    @staticmethod
    def get_quality_activities():
        all_nodes = quality_node.QualityNode.fetch_all_nodes()
        return [node for node in all_nodes if node.type == 'ACT']

    @staticmethod
    def get_non_achieved_activities():
        activities = QualityActivity.get_quality_activities()
        return [activity for activity in activities if activity.achievement != 1]

    def get_bottom_req(self):
        pass