import csv

from app.module_workers.worker import Worker

# Persistencia relacionada con el archivo resources/register_of_Workers.csv 
class WorkersDataCSV:
    def __init__(self, file_path):
        self.file_path = file_path

    # Lee el csv y convierte cada fila a Worker
    def read_workers(self):
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')  # Asegurar delimitador correcto
                workers = []
                for row in reader:
                    # Crea cada trabajador
                    worker = Worker(
                        id=row['id'],
                        workstation=row['workstation'],
                        hiring_date=row['hiring_date'],
                        rol=row['rol'] if row['rol'] else None,
                        register_date=row['register_date'] if row['register_date'] else None
                    )
                    workers.append(worker)
                return workers
        except FileNotFoundError:
            print(f"Archivo no existe.")
            return []

    # Devuelve los ids de los trabajadores que no están dados de alta en el sistema
    def get_workers_no_role(self):
        ids = []
        
        with open(self.file_path, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            for row in reader:
                if 'rol' in row and (row['rol'] is None or row['rol'].strip() == ''):
                    ids.append(row['id'])
        
        return ids

    # Encuentra para un id su trabajador asociado si lo hay
    def find_worker_by_id(self, worker_id):
        with open(self.file_path, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                if 'id' in row:
                    if row['id'] == worker_id:
                        return row
        return None

    # Inserta un trabajador en el fichero
    def insert_worker(self, worker):
        with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'workstation', 'date_contratation', 'rol', 'register_date'], delimiter=';')
            writer.writerow(worker.to_dict())

    # Para un trabajador existente, dado por su id, se modifica su rol y su fecha de alta
    def update_worker(self, worker_id, rol, register_date):
        rows = []
        modified = False
        
        # Leer el archivo y modificar la fila si el id coincide
        with open(self.file_path, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            fieldnames = reader.fieldnames
            
            for row in reader:
                if row.get('id') == worker_id:
                    row['rol'] = rol
                    row['register_date'] = register_date
                    modified = True
                rows.append(row)
        
        # Si se modificó alguna fila, escribir los cambios en el archivo
        if modified:
            with open(self.file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(rows)
        
        return modified

