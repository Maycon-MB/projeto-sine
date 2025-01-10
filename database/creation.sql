-- Tabela: curriculo
DROP TABLE IF EXISTS public.curriculo;

CREATE TABLE IF NOT EXISTS public.curriculo (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    idade INTEGER NOT NULL,
    telefone VARCHAR(15),
    escolaridade VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'disponível' CHECK (status IN ('disponível', 'empregado', 'não disponível'))
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.curriculo
    OWNER TO postgres;

-- Índices para a tabela curriculo
CREATE INDEX IF NOT EXISTS idx_curriculo_status ON public.curriculo (status);
CREATE INDEX IF NOT EXISTS idx_curriculo_nome ON public.curriculo (nome);
CREATE INDEX IF NOT EXISTS idx_curriculo_escolaridade ON public.curriculo (escolaridade);
CREATE INDEX IF NOT EXISTS idx_curriculo_idade ON public.curriculo (idade);

-- Tabela: experiencias
DROP TABLE IF EXISTS public.experiencias;

CREATE TABLE IF NOT EXISTS public.experiencias (
    id SERIAL PRIMARY KEY,
    id_curriculo INTEGER NOT NULL,
    cargo VARCHAR(255) NOT NULL,
    anos_experiencia INTEGER NOT NULL CHECK (anos_experiencia >= 0),
    FOREIGN KEY (id_curriculo) REFERENCES public.curriculo (id) ON DELETE CASCADE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.experiencias
    OWNER TO postgres;

-- Tabela: pessoa_servicos
DROP TABLE IF EXISTS public.pessoa_servicos;

CREATE TABLE IF NOT EXISTS public.pessoa_servicos (
    id SERIAL PRIMARY KEY,
    pessoa_id INTEGER,
    servico VARCHAR(255) NOT NULL,
    FOREIGN KEY (pessoa_id) REFERENCES public.curriculo (id) ON DELETE CASCADE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.pessoa_servicos
    OWNER TO postgres;

-- Tabela: servicos
DROP TABLE IF EXISTS public.servicos;

CREATE TABLE IF NOT EXISTS public.servicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT servicos_nome_key UNIQUE (nome)
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.servicos
    OWNER TO postgres;

-- Tabela: usuarios
DROP TABLE IF EXISTS public.usuarios;

CREATE TABLE IF NOT EXISTS public.usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,  -- Cidade adicionada
    tipo_usuario VARCHAR(20) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT usuarios_email_key UNIQUE (email),
    CONSTRAINT usuarios_usuario_key UNIQUE (usuario),
    CONSTRAINT usuarios_tipo_usuario_check CHECK (tipo_usuario IN ('admin', 'comum'))
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.usuarios
    OWNER TO postgres;

-- Tabela: aprovacoes
DROP TABLE IF EXISTS public.aprovacoes;

CREATE TABLE IF NOT EXISTS public.aprovacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    cidade VARCHAR(100) NOT NULL,  -- Cidade vinculada à aprovação
    status_aprovacao VARCHAR(20) DEFAULT 'pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);

-- Tabela: recuperacao_senha
DROP TABLE IF EXISTS public.recuperacao_senha;

CREATE TABLE IF NOT EXISTS public.recuperacao_senha (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    token VARCHAR(255) NOT NULL,
    expiracao TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);

-- View: vw_curriculos_detalhados
DROP VIEW IF EXISTS public.vw_curriculos_detalhados;

CREATE OR REPLACE VIEW public.vw_curriculos_detalhados AS
SELECT 
    c.id AS curriculo_id,
    c.nome,
    c.idade,
    c.telefone,
    c.escolaridade,
    c.status,
    e.cargo,
    e.anos_experiencia
FROM 
    curriculo c
LEFT JOIN 
    experiencias e 
ON 
    c.id = e.id_curriculo;

ALTER TABLE public.vw_curriculos_detalhados
    OWNER TO postgres;
