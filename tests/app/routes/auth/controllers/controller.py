from fastapi import HTTPException

from app.policies.user_policy import UserPolicy
from app.routes.read.services.service import ReadUserService 

# Controller é responsável por receber a requisição, verificar as permissões e chamar o serviço para processar a lógica de negócio. Ele atua como um intermediário entre a camada de roteamento (FastAPI) e a camada de serviço, garantindo que as regras de autorização sejam aplicadas antes de acessar os dados ou executar qualquer ação.

class ReadUserController:

    def __init__(self):
        self.service = ReadUserService()

    def handle(self, db, request, current_user):

        authorized = UserPolicy.can_view(        #  Verifica se o usuário atual tem permissão para visualizar os dados solicitados, passando a requisição e o usuário atual para a função can_view da classe UserPolicy. A função retorna True ou False com base nas regras de autorização definidas.
            request=request,
            current_user=current_user
        )    

        if not authorized:                       # Se o usuário não estiver autorizado, o controller levanta uma exceção HTTP 403 (Forbidden) usando HTTPException do FastAPI, indicando que o usuário não tem permissão para acessar os dados solicitados.
            raise HTTPException(
                status_code=403, 
                detail="Not authorized"
            )
        
        response = self.service.execute(
            db=db,
            request=request
        )

        return response 