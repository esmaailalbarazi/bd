SET timezone='Europe/Lisbon';

--Inserir na tabela utilizador
INSERT INTO utilizador (idutilizador, username, password, email, authtoken)
VALUES  ('1', 'Teste1', 'asd123', 'teste1@mail.com', '1'),
        ('2', 'Teste2', 'asd123', 'teste2@mail.com', '2'),
        ('3', 'Teste3', 'asd123', 'teste3@mail.com', '3');

--Insere artigos EAN e ISBN
INSERT INTO artigo (idartigo) VALUES ('1');
INSERT INTO artigo (idartigo) VALUES ('2');
INSERT INTO artigo (idartigo) VALUES ('3');
INSERT INTO artigo (idartigo) VALUES ('4');
INSERT INTO artigoean (codigo, artigo_idartigo)
VALUES ('1111111111111', '1'), ('2222222222222', '2');
INSERT INTO artigoisbn (codigo, artigo_idartigo)
VALUES ('3333333333', '3'), ('4444444444', '4');

--Inserir um vendedor e leilão
INSERT INTO vendedor (utilizador_idutilizador) VALUES ('1');
INSERT INTO vendedor (utilizador_idutilizador) VALUES ('2');
INSERT INTO leilao (idleilao, titulo, descricao, datalimite, precominimo, precoatual,
    vendedor_utilizador_idutilizador, artigo_idartigo, terminou)
VALUES ('1', 'Leilão 1', 'Leilão de teste 1', '2021-12-31 20:00', '10', '40', '1', '1', 'false'),
('1', 'Leilão 2', 'Leilão de teste 2', '2021-12-31 20:00', '20', '20', '2', '2', 'false');

--Inserir mensagens no leilão '1'
INSERT INTO mensagem (idmensagem, conteudo, data, utilizador_idutilizador, leilao_idleilao)
VALUES ('1', 'Mensagem de teste 1', '2021-05-30 10:00', '1', '1');
VALUES ('2', 'Mensagem de teste 2', '2021-05-30 12:00', '2', '1');

--Inserir licitações no leilão '1'
INSERT INTO comprador (utilizador_idutilizador) VALUES ('2');
INSERT INTO comprador (utilizador_idutilizador) VALUES ('3');
INSERT INTO licitacao (idlicitacao, valor, data, comprador_utilizador_idutilizador, leilao_idleilao)
VALUES ('1', '20', '2021-05-30 15:00', '2', '1'),
VALUES ('1', '40', '2021-05-30 20:00', '2', '1');
