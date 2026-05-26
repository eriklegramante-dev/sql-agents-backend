from app.routes.read.workflows.workflow import ReadUserWorkflow
from app.routes.read.dto.response import ReadUserResponseDTO

# Service é a conexão entre o controller e o workflow. Ele é responsável por receber as chamadas do controller, processar a lógica de negócio usando o workflow

class ReadUserService:                     # ReadUserService é a classe de serviço responsável por orquestrar a execução do workflow de leitura de usuários. Ela atua como uma camada intermediária entre o controller e o workflow, garantindo que a lógica de negócio seja processada corretamente antes de retornar a resposta ao controller.

    def __init__(self):
        self.workflow = ReadUserWorkflow()

    def execute(self, db, request):

        result = self.workflow.execute(db, request)

        return ReadUserResponseDTO(**result)
    
    