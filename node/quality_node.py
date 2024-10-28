from psycopg2 import Error
from pages.core import write_db


class QualityNode:
    def __init__(self, nid, pid, parents, children, type, subtype, task, achievement, contribution):
        self.nid = nid
        self.pid = pid
        self.parents = parents
        self.children = children
        self.type = type
        self.subtype = subtype
        self.task = task
        self.achievement = achievement
        self.contribution = contribution
    
    @staticmethod
    def get_node_support():
        node_support = []
        connector = None
        cursor = None
        try:
            connector = write_db.get_connector()
            cursor = connector.cursor()
            cursor.execute('SELECT source, destination, contribution FROM support')
            node_support = cursor.fetchall()
        except (Exception, Error) as error:
            print('PostgreSQLへの接続時のエラーが発生しました:', error)
        finally:
            if cursor:
                cursor.close()
            if connector:
                connector.close()
        return node_support

    @classmethod
    def assign_support_to_nodes(cls, nodes, node_support):
        # ノードの辞書を作成して、nidで検索しやすくする
        node_dict = {node.nid: node for node in nodes}
        #デバック用変数
        # count = 0
        for node in nodes:
            #デバック用
            # print(node)
            # count += 1
            # if count == 20:
            #     break
            # destinationがnodeのnidと等しいものを探す
            for support in node_support:
                destination, source, contribution = support
                if destination == node.nid:
                    # print(source)
                    # print(node_dict[source])
                    while source in node_dict and node_dict[source].type != 'REQ':
                        # sourceの値をdestinationに移して再検索
                        next_source = next((s[1] for s in node_support if s[0] == source), None)
                        if next_source is None:
                            #デバック用
                            # print('miss')
                            break
                        source = next_source

                    if source in node_dict and node_dict[source].type == 'REQ':
                        node.parents.append(source)
                        node.contribution.append(contribution)

            # sourceがnodeのnidと等しいものを探す
            for support in node_support:
                destination, source, contribution = support
                if source == node.nid:
                    node.children.append(destination)
            #デバック用
            # print(f"Node {node.nid} parents: {node.parents}, children: {node.children}, type: {node.type}")
        
        return nodes

    
    
    @staticmethod
    def fetch_all_nodes():
        nodes = []
        connector = None
        cursor = None
        try:
            connector = write_db.get_connector()
            cursor = connector.cursor()
            cursor.execute('SELECT * FROM qualitynode')
            records = cursor.fetchall()
            node_support = QualityNode.get_node_support()
            for record in records:
                nid, pid, cid, type, subtype, content, achievement = record
                parents = []
                children = []
                contribution = []
                task = content #仮でcontentを代入

                if type == 'ACT':
                    from node.quality_activity import QualityActivity
                    node = QualityActivity(nid, pid, parents, children, type, subtype, task, achievement, contribution, is_manual=None)
                elif type == 'REQ':
                    from node.quality_requirement import QualityRequirement
                    node = QualityRequirement(nid, pid, parents, children, type, subtype, task, achievement, contribution, req_text=None)
                elif type == 'IMP':
                    from node.quality_implementation import QualityImplementation
                    node = QualityImplementation(nid, pid, parents, children, type, subtype, task, achievement, contribution, description=None)
                else:
                    node = QualityNode(nid, pid, parents, children, type, subtype, task, achievement, contribution)
                nodes.append(node)

            nodes = QualityNode.assign_support_to_nodes(nodes, node_support)

        except (Exception, Error) as error:
            print('PostgreSQLへの接続時のエラーが発生しました:', error)

        finally:
            if cursor:
                cursor.close()
            if connector:
                connector.close()

        return nodes

    def dispatch(self):
        pass
    
class Member:
    def __init__(self, mid, mname, pid, sprint_resource, used_resource, redmine_id):
        self.mid = mid
        self.mname = mname
        self.pid = pid
        self.sprint_resource = sprint_resource
        self.used_resource = used_resource
        self.redmine_id = redmine_id

    @staticmethod
    def fetch_all_members():
        members = []
        connector = None
        cursor = None
        try:
            connector = write_db.get_connector()
            cursor = connector.cursor()
            cursor.execute('SELECT * FROM member')
            records = cursor.fetchall()
            for record in records:
                mid, mname, pid, sprint_resource, used_resource, redmine_id = record
                member = Member(mid, mname, pid, sprint_resource, used_resource, redmine_id)
                members.append(member)
        except (Exception, Error) as error:
            print('PostgreSQLへの接続時のエラーが発生しました:', error)
        finally:
            if cursor:
                cursor.close()
            if connector:
                connector.close()
        return members