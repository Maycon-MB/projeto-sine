-- Apagar o esquema caso exista
DROP SCHEMA IF EXISTS public CASCADE;

-- Criar o esquema novamente
CREATE SCHEMA public;

-- Dropar tabelas caso existam, sem a necessidade de CASCADE
DROP TABLE IF EXISTS public.logs_auditoria;
DROP TABLE IF EXISTS public.notificacoes;
DROP VIEW IF EXISTS public.vw_curriculos_detalhados;
DROP TABLE IF EXISTS public.recuperacao_senha;
DROP TABLE IF EXISTS public.aprovacoes;
DROP TABLE IF EXISTS public.usuarios;
DROP TABLE IF EXISTS public.servicos;
DROP TABLE IF EXISTS public.pessoa_servicos;
DROP TABLE IF EXISTS public.experiencias;
DROP TABLE IF EXISTS public.curriculo;
DROP TABLE IF EXISTS public.cidades;

-- Tabela: cidades
CREATE TABLE public.cidades (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
)
TABLESPACE pg_default;

ALTER TABLE public.cidades
    OWNER TO postgres;

-- Populando a tabela cidades com nomes das cidades do RJ
INSERT INTO public.cidades (nome)
VALUES
    ('ANGRA DOS REIS'),
    ('APERIBÉ'),
    ('ARARUAMA'),
    ('AREAL'),
    ('ARMAÇÃO DOS BÚZIOS'),
    ('ARRAIAL DO CABO'),
    ('BARRA DO PIRAÍ'),
    ('BARRA MANSA'),
    ('BELFORD ROXO'),
    ('BOM JARDIM'),
    ('BOM JESUS DO ITABAPOANA'),
    ('CABO FRIO'),
    ('CACHOEIRAS DE MACACU'),
    ('CAMBUCI'),
    ('CAMPOS DOS GOYTACAZES'),
    ('CANTAGALO'),
    ('CARAPEBUS'),
    ('CARDOSO MOREIRA'),
    ('CARMO'),
    ('CASIMIRO DE ABREU'),
    ('COMENDADOR LEVY GASPARIAN'),
    ('CONCEIÇÃO DE MACABU'),
    ('CORDEIRO'),
    ('DUAS BARRAS'),
    ('DUQUE DE CAXIAS'),
    ('ENGENHEIRO PAULO DE FRONTIN'),
    ('GUAPIMIRIM'),
    ('IGUABA GRANDE'),
    ('ITABORAÍ'),
    ('ITAGUAÍ'),
    ('ITALVA'),
    ('ITAOCARA'),
    ('ITAPERUNA'),
    ('ITATIAIA'),
    ('JAPERI'),
    ('LAJE DO MURIAÉ'),
    ('MACAÉ'),
    ('MACUCO'),
    ('MAGÉ'),
    ('MANGARATIBA'),
    ('MARICÁ'),
    ('MENDES'),
    ('MESQUITA'),
    ('MIGUEL PEREIRA'),
    ('MIRACEMA'),
    ('NATIVIDADE'),
    ('NILÓPOLIS'),
    ('NITERÓI'),
    ('NOVA FRIBURGO'),
    ('NOVA IGUAÇU'),
    ('PARACAMBI'),
    ('PARAÍBA DO SUL'),
    ('PARATY'),
    ('PATY DO ALFERES'),
    ('PETRÓPOLIS'),
    ('PINHEIRAL'),
    ('PIRAI'),
    ('PORCIÚNCULA'),
    ('PORTO REAL'),
    ('QUATIS'),
    ('QUEIMADOS'),
    ('QUISSAMÃ'),
    ('RESENDE'),
    ('RIO BONITO'),
    ('RIO CLARO'),
    ('RIO DAS FLORES'),
    ('RIO DAS OSTRAS'),
    ('RIO DE JANEIRO'),
    ('SANTA MARIA MADALENA'),
    ('SANTO ANTÔNIO DE PÁDUA'),
    ('SÃO FIDÉLIS'),
    ('SÃO FRANCISCO DE ITABAPOANA'),
    ('SÃO GONÇALO'),
    ('SÃO JOÃO DA BARRA'),
    ('SÃO JOÃO DE MERITI'),
    ('SÃO JOSÉ DE UBÁ'),
    ('SÃO JOSÉ DO VALE DO RIO PRETO'),
    ('SÃO PEDRO DA ALDEIA'),
    ('SÃO SEBASTIÃO DO ALTO'),
    ('SAPUCÁIA'),
    ('SAQUAREMA'),
    ('SEROPÉDICA'),
    ('SILVA JARDIM'),
    ('SUMIDOURO'),
    ('TANGUÁ'),
    ('TERESÓPOLIS'),
    ('TRAJANO DE MORAES'),
    ('TRÊS RIOS'),
    ('VALENÇA'),
    ('VARRE-SAI'),
    ('VASSOURAS'),
    ('VOLTA REDONDA')
ON CONFLICT DO NOTHING;

-- Tabela: curriculo
CREATE TABLE public.curriculo (
    id SERIAL PRIMARY KEY,
    cpf CHAR(11) NOT NULL UNIQUE CHECK (cpf ~ '^\d{11}$'),
    nome VARCHAR(255) NOT NULL,
    sexo VARCHAR(9) NOT NULL CHECK (sexo IN ('MASCULINO', 'FEMININO')),
    data_nascimento DATE NOT NULL,
    cidade_id INTEGER NOT NULL,
    telefone VARCHAR(11) CHECK (telefone ~ '^\d{10,11}$'),
    telefone_extra VARCHAR(11) CHECK (telefone_extra ~ '^\d{10,11}$'),
    escolaridade VARCHAR(255) NOT NULL,
    tem_ctps BOOLEAN DEFAULT FALSE,
    servico VARCHAR(6) NOT NULL CHECK (servico IN ('SINE', 'MANUAL')),
    vaga_encaminhada BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_curriculo_cidade FOREIGN KEY (cidade_id) REFERENCES public.cidades (id)
)
TABLESPACE pg_default;

ALTER TABLE public.curriculo
    OWNER TO postgres;

-- Índices para a tabela curriculo
CREATE INDEX IF NOT EXISTS idx_curriculo_cpf ON public.curriculo (cpf);
CREATE INDEX IF NOT EXISTS idx_curriculo_nome ON public.curriculo (nome);
CREATE INDEX IF NOT EXISTS idx_curriculo_escolaridade ON public.curriculo (escolaridade);
CREATE INDEX IF NOT EXISTS idx_curriculo_cidade ON public.curriculo (cidade_id);

-- Tabela: experiencias
CREATE TABLE public.experiencias (
    id SERIAL PRIMARY KEY,
    id_curriculo INTEGER NOT NULL,
    cargo VARCHAR(255) NOT NULL,
    anos_experiencia INTEGER NOT NULL CHECK (anos_experiencia >= 0),
    meses_experiencia INTEGER NOT NULL CHECK (meses_experiencia >= 0 AND meses_experiencia < 12),
    FOREIGN KEY (id_curriculo) REFERENCES public.curriculo (id) ON DELETE CASCADE
)
TABLESPACE pg_default;

ALTER TABLE public.experiencias
    OWNER TO postgres;

-- Tabela: pessoa_servicos
CREATE TABLE public.pessoa_servicos (
    id SERIAL PRIMARY KEY,
    pessoa_id INTEGER,
    servico VARCHAR(255) NOT NULL,
    FOREIGN KEY (pessoa_id) REFERENCES public.curriculo (id) ON DELETE CASCADE
)
TABLESPACE pg_default;

ALTER TABLE public.pessoa_servicos
    OWNER TO postgres;

-- Tabela: servicos
CREATE TABLE public.servicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT servicos_nome_key UNIQUE (nome)
)
TABLESPACE pg_default;

ALTER TABLE public.servicos
    OWNER TO postgres;

-- Tabela: usuarios
CREATE TABLE public.usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    tipo_usuario VARCHAR(20) NOT NULL CHECK (tipo_usuario IN ('admin', 'comum', 'master')), 
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT usuarios_email_key UNIQUE (email),
    CONSTRAINT usuarios_usuario_key UNIQUE (usuario)
)
TABLESPACE pg_default;

ALTER TABLE public.usuarios
    OWNER TO postgres;

-- Tabela: aprovacoes
CREATE TABLE public.aprovacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    status_aprovacao VARCHAR(20) DEFAULT 'pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);

-- Tabela: recuperacao_senha
CREATE TABLE public.recuperacao_senha (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    token VARCHAR(255) NOT NULL,
    expiracao TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);

-- View: vw_curriculos_detalhados
CREATE OR REPLACE VIEW public.vw_curriculos_detalhados AS
SELECT 
    c.id AS curriculo_id,
    c.cpf,
    c.nome,
    c.sexo,
    c.data_nascimento,
    DATE_PART('year', AGE(c.data_nascimento)) AS idade,
    ci.nome AS cidade,
    c.telefone,
    c.telefone_extra,
    c.escolaridade,
    c.tem_ctps,
    c.servico,
    c.vaga_encaminhada,
    e.cargo,
    e.anos_experiencia,
    e.meses_experiencia
FROM 
    curriculo c
LEFT JOIN 
    experiencias e 
ON 
    c.id = e.id_curriculo
LEFT JOIN
    cidades ci ON c.cidade_id = ci.id;

ALTER TABLE public.vw_curriculos_detalhados
    OWNER TO postgres;

-- Nova tabela: notificacoes
CREATE TABLE public.notificacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    evento VARCHAR(255) NOT NULL,
    descricao TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lido BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);

-- Índices para melhorar consultas na tabela notificacoes
CREATE INDEX IF NOT EXISTS idx_notificacoes_usuario_id ON public.notificacoes (usuario_id);
CREATE INDEX IF NOT EXISTS idx_notificacoes_evento ON public.notificacoes (evento);
CREATE INDEX IF NOT EXISTS idx_notificacoes_lido ON public.notificacoes (lido);

-- Tabela: logs_auditoria
CREATE TABLE public.logs_auditoria (
    id SERIAL PRIMARY KEY,
    notificacao_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    acao VARCHAR(20) NOT NULL CHECK (acao IN ('aprovado', 'rejeitado')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notificacao_id) REFERENCES public.aprovacoes (id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES public.usuarios (id) ON DELETE CASCADE
);
