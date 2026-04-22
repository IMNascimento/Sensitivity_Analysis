import gsi
from google.protobuf import json_format

class SeepExplorer:
    def __init__(self, project_path: str, analysis_name: str):
        self.project_path = project_path
        self.analysis_name = analysis_name
        self.project = None

    def open(self):
        if self.project is None:
            print("[DEBUG] Abrindo projeto...")
            self.project = gsi.OpenProject(self.project_path)
            print("[DEBUG] Projeto aberto.")

    def get_object(self, object_path: str):
        if self.project is None:
            self.open()

        print(f"[DEBUG] Get: {object_path}")
        response = self.project.Get(
            gsi.GetRequest(
                analysis=self.analysis_name,
                object=object_path,
            )
        )
        data = json_format.MessageToDict(response)
        print(data)
        return data

    def close(self):
        if self.project is not None:
            print("[DEBUG] Fechando projeto...")
            self.project.Close()
            self.project = None
            print("[DEBUG] Projeto fechado.")