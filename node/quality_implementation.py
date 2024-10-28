from . import quality_node

class QualityImplementation(quality_node.QualityNode):
    def __init__(self, nid, pid, parents, children, type, subtype, task, achievement, contribution, description):
        super().__init__(nid, pid, parents, children, type, subtype, task, achievement, contribution)
        self.description = description

    #デバック用
    def __str__(self):
        return f'QualityImplementation(nid={self.nid}, type={self.type})'
    @staticmethod
    def get_quality_implementations():
        all_nodes = quality_node.QualityNode.fetch_all_nodes()
        return [node for node in all_nodes if node.type == 'IMP']


class Function(QualityImplementation):
    pass


class Architecture(QualityImplementation):
    pass