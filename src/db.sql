CREATE TABLE utilizador (
	idutilizador SERIAL,
	username	 VARCHAR(32) UNIQUE NOT NULL,
	password	 VARCHAR(128) NOT NULL,
	email	 VARCHAR(64) UNIQUE NOT NULL,
	authtoken	VARCHAR(128) UNIQUE
	PRIMARY KEY(idutilizador)
);

CREATE TABLE vendedor (
	utilizador_idutilizador BIGINT,
	PRIMARY KEY(utilizador_idutilizador)
);

CREATE TABLE comprador (
	utilizador_idutilizador BIGINT,
	PRIMARY KEY(utilizador_idutilizador)
);

CREATE TABLE leilao (
	idleilao			 SERIAL,
	titulo				 VARCHAR(64) NOT NULL,
	descricao			 TEXT NOT NULL,
	datalimite			 DATE NOT NULL,
	precominimo			 FLOAT(8) NOT NULL,
	precoatual			 FLOAT(8) NOT NULL,
	vendedor_utilizador_idutilizador BIGINT NOT NULL,
	artigo_idartigo			 BIGINT NOT NULL,
	PRIMARY KEY(idleilao)
);

CREATE TABLE artigo (
	idartigo SERIAL UNIQUE,
	PRIMARY KEY(idartigo)
);

CREATE TABLE licitacao (
	idlicitacao			 SERIAL,
	valor				 FLOAT(8),
	data				 DATE NOT NULL,
	milisegundos			 INTEGER,
	comprador_utilizador_idutilizador BIGINT NOT NULL,
	leilao_idleilao			 BIGINT NOT NULL,
	PRIMARY KEY(idlicitacao)
);

CREATE TABLE artigoean (
	codigo		 VARCHAR(13) UNIQUE NOT NULL,
	artigo_idartigo BIGINT UNIQUE,
	PRIMARY KEY(artigo_idartigo)
);

CREATE TABLE artigoisbn (
	codigo		 VARCHAR(13) UNIQUE NOT NULL,
	artigo_idartigo BIGINT UNIQUE,
	PRIMARY KEY(artigo_idartigo)
);

CREATE TABLE mensagem (
	idmensagem		 SERIAL,
	conteudo		 TEXT NOT NULL,
	utilizador_idutilizador BIGINT NOT NULL,
	leilao_idleilao	 BIGINT NOT NULL,
	PRIMARY KEY(idmensagem)
);

CREATE TABLE notificacao (
	texto			 TEXT,
	data			 DATE NOT NULL,
	utilizador_idutilizador BIGINT,
	PRIMARY KEY(utilizador_idutilizador)
);

CREATE TABLE notificacaolicitacao (
	licitacao_idlicitacao		 BIGINT,
	notificacao_utilizador_idutilizador BIGINT,
	PRIMARY KEY(notificacao_utilizador_idutilizador)
);

CREATE TABLE notificacaomensagem (
	mensagem_idmensagem		 BIGINT,
	notificacao_utilizador_idutilizador BIGINT,
	PRIMARY KEY(notificacao_utilizador_idutilizador)
);

ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (utilizador_idutilizador) REFERENCES utilizador(idutilizador);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (utilizador_idutilizador) REFERENCES utilizador(idutilizador);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (vendedor_utilizador_idutilizador) REFERENCES vendedor(utilizador_idutilizador);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (artigo_idartigo) REFERENCES artigo(idartigo);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (comprador_utilizador_idutilizador) REFERENCES comprador(utilizador_idutilizador);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (leilao_idleilao) REFERENCES leilao(idleilao);
ALTER TABLE artigoean ADD CONSTRAINT artigoean_fk1 FOREIGN KEY (artigo_idartigo) REFERENCES artigo(idartigo);
ALTER TABLE artigoisbn ADD CONSTRAINT artigoisbn_fk1 FOREIGN KEY (artigo_idartigo) REFERENCES artigo(idartigo);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (utilizador_idutilizador) REFERENCES utilizador(idutilizador);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk2 FOREIGN KEY (leilao_idleilao) REFERENCES leilao(idleilao);
ALTER TABLE notificacao ADD CONSTRAINT notificacao_fk1 FOREIGN KEY (utilizador_idutilizador) REFERENCES utilizador(idutilizador);
ALTER TABLE notificacaolicitacao ADD CONSTRAINT notificacaolicitacao_fk1 FOREIGN KEY (licitacao_idlicitacao) REFERENCES licitacao(idlicitacao);
ALTER TABLE notificacaolicitacao ADD CONSTRAINT notificacaolicitacao_fk2 FOREIGN KEY (notificacao_utilizador_idutilizador) REFERENCES notificacao(utilizador_idutilizador);
ALTER TABLE notificacaomensagem ADD CONSTRAINT notificacaomensagem_fk1 FOREIGN KEY (mensagem_idmensagem) REFERENCES mensagem(idmensagem);
ALTER TABLE notificacaomensagem ADD CONSTRAINT notificacaomensagem_fk2 FOREIGN KEY (notificacao_utilizador_idutilizador) REFERENCES notificacao(utilizador_idutilizador);


