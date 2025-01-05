-- View: public.vw_curriculos_detalhados

-- DROP VIEW public.vw_curriculos_detalhados;

CREATE OR REPLACE VIEW public.vw_curriculos_detalhados
 AS
 SELECT c.id AS curriculo_id,
    c.nome,
    c.idade,
    c.telefone,
    c.escolaridade,
    e.cargo,
    e.anos_experiencia
   FROM curriculo c
     LEFT JOIN experiencias e ON c.id = e.id_curriculo;

ALTER TABLE public.vw_curriculos_detalhados
    OWNER TO postgres;


-- Table: public.curriculo

-- DROP TABLE IF EXISTS public.curriculo;

CREATE TABLE IF NOT EXISTS public.curriculo
(
    id integer NOT NULL DEFAULT nextval('pessoas_id_seq'::regclass),
    nome character varying(255) COLLATE pg_catalog."default" NOT NULL,
    idade integer NOT NULL,
    telefone character varying(15) COLLATE pg_catalog."default",
    escolaridade character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pessoas_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.curriculo
    OWNER to postgres;
-- Index: idx_curriculo_escolaridade

-- DROP INDEX IF EXISTS public.idx_curriculo_escolaridade;

CREATE INDEX IF NOT EXISTS idx_curriculo_escolaridade
    ON public.curriculo USING btree
    (escolaridade COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_curriculo_idade

-- DROP INDEX IF EXISTS public.idx_curriculo_idade;

CREATE INDEX IF NOT EXISTS idx_curriculo_idade
    ON public.curriculo USING btree
    (idade ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_curriculo_nome

-- DROP INDEX IF EXISTS public.idx_curriculo_nome;

CREATE INDEX IF NOT EXISTS idx_curriculo_nome
    ON public.curriculo USING btree
    (nome COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.experiencias

-- DROP TABLE IF EXISTS public.experiencias;

CREATE TABLE IF NOT EXISTS public.experiencias
(
    id integer NOT NULL DEFAULT nextval('experiencias_id_seq'::regclass),
    id_curriculo integer NOT NULL,
    cargo character varying(255) COLLATE pg_catalog."default" NOT NULL,
    anos_experiencia integer NOT NULL,
    CONSTRAINT experiencias_pkey PRIMARY KEY (id),
    CONSTRAINT experiencias_id_curriculo_fkey FOREIGN KEY (id_curriculo)
        REFERENCES public.curriculo (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT experiencias_anos_experiencia_check CHECK (anos_experiencia >= 0)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.experiencias
    OWNER to postgres;

-- Table: public.pessoa_servicos

-- DROP TABLE IF EXISTS public.pessoa_servicos;

CREATE TABLE IF NOT EXISTS public.pessoa_servicos
(
    id integer NOT NULL DEFAULT nextval('pessoa_servicos_id_seq'::regclass),
    pessoa_id integer,
    servico character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pessoa_servicos_pkey PRIMARY KEY (id),
    CONSTRAINT pessoa_servicos_pessoa_id_fkey FOREIGN KEY (pessoa_id)
        REFERENCES public.curriculo (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pessoa_servicos
    OWNER to postgres;

-- Table: public.servicos

-- DROP TABLE IF EXISTS public.servicos;

CREATE TABLE IF NOT EXISTS public.servicos
(
    id integer NOT NULL DEFAULT nextval('servicos_id_seq'::regclass),
    nome character varying(100) COLLATE pg_catalog."default" NOT NULL,
    descricao text COLLATE pg_catalog."default",
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT servicos_pkey PRIMARY KEY (id),
    CONSTRAINT servicos_nome_key UNIQUE (nome)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.servicos
    OWNER to postgres;

-- Table: public.usuarios

-- DROP TABLE IF EXISTS public.usuarios;

CREATE TABLE IF NOT EXISTS public.usuarios
(
    id integer NOT NULL DEFAULT nextval('usuarios_id_seq'::regclass),
    usuario character varying(50) COLLATE pg_catalog."default" NOT NULL,
    senha_hash character varying(255) COLLATE pg_catalog."default" NOT NULL,
    email character varying(100) COLLATE pg_catalog."default" NOT NULL,
    tipo_usuario character varying(20) COLLATE pg_catalog."default" NOT NULL,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT usuarios_pkey PRIMARY KEY (id),
    CONSTRAINT usuarios_email_key UNIQUE (email),
    CONSTRAINT usuarios_usuario_key UNIQUE (usuario),
    CONSTRAINT usuarios_tipo_usuario_check CHECK (tipo_usuario::text = ANY (ARRAY['admin'::character varying, 'comum'::character varying]::text[]))
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.usuarios
    OWNER to postgres;

CREATE TABLE IF NOT EXISTS public.aprovacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    status_aprovacao VARCHAR(20) DEFAULT 'pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.recuperacao_senha (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    token VARCHAR(255) NOT NULL,
    expiracao TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);
