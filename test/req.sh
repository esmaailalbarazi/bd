echo 'Carregar enter para realizar as seguintes ações:'
read -p 'Registar utlizador "João"'
curl -X POST 127.0.0.1:8080/dbproj/user -d @registo1.json --header "Content-Type: application/json"
read -p 'Registar utlizador "Pedro"'
curl -X POST 127.0.0.1:8080/dbproj/user -d @registo1.json --header "Content-Type: application/json"
read -p 'Autenticar utlizador "João"'
curl -X PUT 127.0.0.1:8080/dbproj/user -d @login1.json --header "Content-Type: application/json"
read -p 'Autenticar utlizador "João"'
curl -X PUT 127.0.0.1:8080/dbproj/user -d @login2.json --header "Content-Type: application/json"
read -p 'Criar leilão Frigorifico usado'
curl -X POST 127.0.0.1:8080/dbproj/leilao -d @leilao1.json --header "Content-Type: application/json"
read -p 'Criar leilão Carro novo'
curl -X POST 127.0.0.1:8080/dbproj/leilao -d @leilao2.json --header "Content-Type: application/json"
read -p 'Listar leilões'
curl -X GET 127.0.0.1:8080/dbproj/leiloes -d --header "Content-Type: application/json"
read -p 'Pesquisar um leilão por id'
curl -X GET 127.0.0.1:8080/dbproj/leiloes/8 -d  --header "Content-Type: application/json"
read -p 'Pesquisar um leilão por keyword'
curl -X GET 127.0.0.1:8080/dbproj/leiloes/carro -d  --header "Content-Type: application/json"
read -p 'listar leilões onde o utilizador tenha atividade'
curl -X GET 127.0.0.1:8080/dbproj/leilao/1 -d  --header "Content-Type: application/json"
read -p 'nova licitação1'
curl -X POST 127.0.0.1:8080/dbproj/licitar/8 -d @novaLicitacao.json --header "Content-Type: application/json"
read -p 'nova licitação2'
curl -X POST 127.0.0.1:8080/dbproj/licitar/8 -d @novaLicitacao2.json --header "Content-Type: application/json"
read -p 'Editar leilão "Leilão 1"'
curl -X PUT 127.0.0.1:8080/dbproj/leilao/8 -d @editLeilao.json --header "Content-Type: application/json"
read -p 'Editar leilão "Leilão 2"'
curl -X PUT 127.0.0.1:8080/dbproj/leilao/8 -d @editLeilao.json --header "Content-Type: application/json"
read -p 'Criar mensagem 1'
curl -X POST 127.0.0.1:8080/dbproj/leilao -d @novaMensagem.json --header "Content-Type: application/json"
read -p 'Criar mensagem 2'
curl -X POST 127.0.0.1:8080/dbproj/leilao -d @novaMensagem2.json --header "Content-Type: application/json"
read -p 'Listar notificações'
curl -X GET 127.0.0.1:8080/dbproj/notificacoes -d @token.json --header "Content-Type: application/json"
read -p 'Terminar leilão 1'
curl -X PUT 127.0.0.1:8080/dbproj/leilao/8/end -d  --header "Content-Type: application/json"
read -p 'Terminar leilão 2'
curl -X PUT 127.0.0.1:8080/dbproj/leilao/8/end -d  --header "Content-Type: application/json"
