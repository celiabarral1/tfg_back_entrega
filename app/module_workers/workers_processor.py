
"""
Entidad como capa de procesador entre el acceso al archivo de trabajadores
y los endpoints
"""
class WorkersProcessor:
    def __init__(self, data_source):
        self.data = data_source

    def read_workers(self):
        self.data.read_workers()

    def get_workers_no_role(self):
        return self.data.get_workers_no_role()

    def find_worker_by_id(self, worker_id):
        return self.data.find_worker_by_id(worker_id)

    def insert_worker(self, worker):
        print('viene a insertar')
        self.data.insert_worker(worker)

    def update_worker(self, worker_id, rol, register_date):
        return self.data.update_worker(worker_id, rol, register_date) 

