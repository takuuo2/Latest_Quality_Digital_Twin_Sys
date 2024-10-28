from psycopg2 import Error
from pages.core import write_db
class Task:
    def __init__(self, tid, tname, nid, cost, parameter):
        self.tid = tid
        self.tname = tname
        self.nid = nid
        self.cost = cost
        self.parameter = parameter

    @staticmethod
    def fetch_all_tasks():
        tasks = []
        connector = None
        cursor = None
        try:
            connector = write_db.get_connector()
            cursor = connector.cursor()
            cursor.execute('SELECT * FROM task')
            records = cursor.fetchall()
            for record in records:
                tid, tname, nid, cost, parameter = record
                task = Task(tid, tname, nid, cost, parameter)
                tasks.append(task)
        except (Exception, Error) as error:
            print('PostgreSQLへの接続時のエラーが発生しました:', error)
        finally:
            if cursor:
                cursor.close()
            if connector:
                connector.close()
        return tasks
    def calculate_cost(self):
        # Implementation of cost method
        pass  # Placeholder for the method implementation

class ManualTask(Task):
    def __init__(self, tid, name, nid, cost, parameter, assigned_to):
        super().__init__(tid, name, nid, cost, parameter)
        self.assigned_to = assigned_to

class FuncTesting(ManualTask):
    pass


class NonFuncTesting(Task):
    def cost(self):
        # Implementation of cost method for NonFuncTesting
        pass  # Placeholder for the method implementation

class TaskAssignment:
    def __init__(self, aid, tid, mid):
        self.aid = aid
        self.tid = tid
        self.mid = mid

    @staticmethod
    def fetch_all_assignments():
        assignments = []
        connector = None
        cursor = None
        try:
            connector = write_db.get_connector()
            cursor = connector.cursor()
            cursor.execute('SELECT * FROM task_assignment')
            records = cursor.fetchall()
            for record in records:
                aid, tid, mid = record
                assignment = TaskAssignment(aid, tid, mid)
                assignments.append(assignment)
        except (Exception, Error) as error:
            print('PostgreSQLへの接続時のエラーが発生しました:', error)
        finally:
            if cursor:
                cursor.close()
            if connector:
                connector.close()
        return assignments
