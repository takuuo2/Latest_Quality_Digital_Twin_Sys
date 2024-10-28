from . import quality_node

class QualityRequirement(quality_node.QualityNode):
    def __init__(self, nid, pid, parents, children, type, subtype, task, achievement, contribution, req_text):
        super().__init__(nid, pid, parents, children, type, subtype, task, achievement, contribution)
        self.req_text = req_text

    #デバック用
    def __str__(self):
        return f'QualityRequirement(nid={self.nid}, type={self.type}, task={self.task})'
    @staticmethod
    def get_quality_requirements():
        all_nodes = quality_node.QualityNode.fetch_all_nodes()
        return [node for node in all_nodes if node.type == 'REQ']
    



class QiURequirement(QualityRequirement):
    def __init__(self, nid, pid, parents, children, type, subtype, task, achievement, contribution, req_text, qiu_char):
        super().__init__(nid, pid, parents, children, type, subtype, task, achievement, contribution, req_text)
        self.qiu_char = qiu_char


class PQRequirement(QualityRequirement):
    def __init__(self, nid, pid, parents, children, type, subtype, task, achievement, contribution, req_text, pq_char):
        super().__init__(nid, pid, parents, children, type, subtype, task, achievement, contribution, req_text)
        self.pq_char = pq_char

