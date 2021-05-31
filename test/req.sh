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
