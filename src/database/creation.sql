-- Apagar o esquema caso exista
DROP SCHEMA IF EXISTS public CASCADE; 

-- Criar o esquema novamente
CREATE SCHEMA public;  

-- Dropar tabelas e views caso existam
DROP TABLE IF EXISTS public.logs_auditoria; 
DROP VIEW IF EXISTS public.vw_curriculos_detalhados; 
DROP TABLE IF EXISTS public.usuarios; 
DROP TABLE IF EXISTS public.experiencias; 
DROP TABLE IF EXISTS public.curriculo; 
DROP TABLE IF EXISTS public.cidades; 
DROP TABLE IF EXISTS public.funcoes; 

-- Tabela: cidades
CREATE TABLE public.cidades (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
) TABLESPACE pg_default;

ALTER TABLE public.cidades
    OWNER TO postgres;

-- Populando a tabela cidades com nomes das cidades do RJ
INSERT INTO public.cidades (nome) VALUES
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
    ('VOLTA REDONDA') ON CONFLICT DO NOTHING;

-- Tabela: funcoes (cargos)
CREATE TABLE public.funcoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
) TABLESPACE pg_default;

ALTER TABLE public.funcoes
    OWNER TO postgres;

-- Populando a tabela funcoes com algumas funções padrão
INSERT INTO public.funcoes (nome) VALUES
    ('AUXILIAR DE LIMPEZA'),
    ('AJUDANTE DE COZINHA'),
    ('ATENDENTE DE LOJA'),
    ('ATENDENTE DE LANCHONETE'),
    ('AUXILIAR DE PRODUÇÃO'),
    ('AUXILIAR DE LOGÍSTICA'),
    ('CAIXA'),
    ('CONSULTOR DE VENDAS'),
    ('COZINHEIRO'),
    ('EMPACOTADOR'),
    ('EMPREGADO DOMÉSTICO'),
    ('ESTOQUISTA'),
    ('FISCAL DE LOJA'),
    ('FISCAL DE PREVENÇÃO DE PERDAS'),
    ('GARÇOM') ON CONFLICT DO NOTHING;

-- Tabela: curriculo
CREATE TABLE public.curriculo (
    id SERIAL PRIMARY KEY,
    cpf CHAR(11) NOT NULL UNIQUE CHECK (cpf ~ '^\d{11}$'),
    nome VARCHAR(255) NOT NULL,
    sexo VARCHAR(9) NOT NULL CHECK (sexo IN ('MASCULINO', 'FEMININO')),
    data_nascimento DATE NOT NULL,
    cidade_id INTEGER NOT NULL,
    telefone VARCHAR(11) CHECK (telefone ~ '^\d{10,11}$'),
    telefone_extra VARCHAR(11) CHECK (telefone_extra ~ '^\d{10,11}$' OR telefone_extra = '' OR telefone_extra IS NULL),
    escolaridade VARCHAR(255) NOT NULL,
    tem_ctps BOOLEAN DEFAULT FALSE,
    cep CHAR(8) CHECK (cep ~ '^\d{8}$'),
    pcd BOOLEAN DEFAULT FALSE,
    data_cadastro TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_curriculo_cidade FOREIGN KEY (cidade_id) REFERENCES public.cidades (id)
) TABLESPACE pg_default;

ALTER TABLE public.curriculo
    OWNER TO postgres;

-- Índices para a tabela curriculo
CREATE INDEX IF NOT EXISTS idx_curriculo_cpf ON public.curriculo (cpf);
CREATE INDEX IF NOT EXISTS idx_curriculo_nome ON public.curriculo (nome);
CREATE INDEX IF NOT EXISTS idx_curriculo_escolaridade ON public.curriculo (escolaridade);
CREATE INDEX IF NOT EXISTS idx_curriculo_cidade ON public.curriculo (cidade_id);

-- Tabela: experiencias (com restrição de unicidade e referenciando a tabela funcoes)
CREATE TABLE public.experiencias (
    id SERIAL PRIMARY KEY,
    id_curriculo INTEGER NOT NULL,
    funcao_id INTEGER NOT NULL,
    anos_experiencia INTEGER NOT NULL CHECK (anos_experiencia >= 0),
    meses_experiencia INTEGER NOT NULL CHECK (meses_experiencia >= 0 AND meses_experiencia < 12),
    FOREIGN KEY (id_curriculo) REFERENCES public.curriculo (id) ON DELETE CASCADE,
    FOREIGN KEY (funcao_id) REFERENCES public.funcoes (id) ON DELETE CASCADE,
    CONSTRAINT unique_id_curriculo_funcao UNIQUE (id_curriculo, funcao_id)
) TABLESPACE pg_default;

ALTER TABLE public.experiencias
    OWNER TO postgres;

-- Tabela: usuarios
CREATE TABLE public.usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    cidade_id INTEGER NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT usuarios_email_key UNIQUE (email),
    CONSTRAINT usuarios_usuario_key UNIQUE (usuario),
    CONSTRAINT fk_usuarios_cidade FOREIGN KEY (cidade_id) REFERENCES public.cidades (id)
) TABLESPACE pg_default;

ALTER TABLE public.usuarios
    OWNER TO postgres;

-- View: vw_curriculos_detalhados
CREATE OR REPLACE VIEW public.vw_curriculos_detalhados AS
SELECT
    c.id AS curriculo_id,
    DATE_PART('year', AGE(c.data_nascimento)) AS idade,
    ci.nome AS cidade,
    c.escolaridade,
    c.tem_ctps,
    c.cep,
    c.pcd,
    f.nome AS funcao,
    e.anos_experiencia,
    e.meses_experiencia
FROM
    curriculo c
LEFT JOIN
    experiencias e ON c.id = e.id_curriculo
LEFT JOIN
    cidades ci ON c.cidade_id = ci.id
LEFT JOIN
    funcoes f ON e.funcao_id = f.id;

ALTER TABLE public.vw_curriculos_detalhados
    OWNER TO postgres;

-- Removendo a função existente, caso já tenha sido criada
DROP FUNCTION IF EXISTS public.filtrar_curriculos(
    TEXT, TEXT, TEXT, TEXT, BOOLEAN, TEXT, INTEGER, INTEGER, INTEGER, INTEGER,
    TEXT, TEXT, TEXT, BOOLEAN, TEXT, TEXT, INTEGER, INTEGER
);

-- Criando a função novamente
CREATE OR REPLACE FUNCTION public.filtrar_curriculos(
    p_nome TEXT DEFAULT NULL,
    p_cidade TEXT DEFAULT NULL,
    p_escolaridade TEXT DEFAULT NULL,
    p_funcao TEXT DEFAULT NULL,
    p_tem_ctps BOOLEAN DEFAULT NULL,
    p_idade_min INTEGER DEFAULT NULL,
    p_idade_max INTEGER DEFAULT NULL,
    p_experiencia INTEGER DEFAULT NULL,
    p_sexo TEXT DEFAULT NULL,
    p_cpf TEXT DEFAULT NULL,
    p_cep TEXT DEFAULT NULL,
    p_pcd BOOLEAN DEFAULT NULL,
    p_telefone TEXT DEFAULT NULL,
    p_telefone_extra TEXT DEFAULT NULL
) 
RETURNS TABLE (
    curriculo_id INTEGER,
    cpf CHAR(11),
    nome TEXT,
    idade INTEGER,
    telefone TEXT,
    telefone_extra TEXT,
    cidade TEXT,
    escolaridade TEXT,
    tem_ctps TEXT,
    cep TEXT,
    pcd BOOLEAN,
    funcao TEXT,
    anos_experiencia INTEGER,
    meses_experiencia INTEGER
) 
AS $$
BEGIN
    RETURN QUERY
    WITH curriculos_base AS (
        SELECT DISTINCT c.id
        FROM curriculo c
        LEFT JOIN cidades ci ON c.cidade_id = ci.id
        WHERE
            (p_nome IS NULL OR c.nome ILIKE '%' || p_nome || '%') AND
            (p_cidade IS NULL OR ci.nome ILIKE '%' || p_cidade || '%') AND
            (p_escolaridade IS NULL OR c.escolaridade = p_escolaridade) AND
            (p_tem_ctps IS NULL OR c.tem_ctps = p_tem_ctps) AND
            (p_idade_min IS NULL OR FLOOR(DATE_PART('year', AGE(c.data_nascimento)))::INT >= p_idade_min) AND
            (p_idade_max IS NULL OR FLOOR(DATE_PART('year', AGE(c.data_nascimento)))::INT <= p_idade_max) AND
            (p_sexo IS NULL OR c.sexo = p_sexo) AND
            (p_cpf IS NULL OR c.cpf = p_cpf) AND
            (p_cep IS NULL OR c.cep = p_cep) AND
            (p_pcd IS NULL OR c.pcd = p_pcd) AND
            (p_telefone IS NULL OR TRIM(c.telefone) LIKE '%' || TRIM(p_telefone) || '%') AND
            (p_telefone_extra IS NULL OR TRIM(c.telefone_extra) LIKE '%' || TRIM(p_telefone_extra) || '%')
    ),
    ranked_experiencias AS (
        SELECT 
            c.id AS curriculo_id,
            f.nome AS funcao,
            e.anos_experiencia,
            e.meses_experiencia,
            ROW_NUMBER() OVER (
                PARTITION BY c.id 
                ORDER BY (e.anos_experiencia * 12 + e.meses_experiencia) DESC
            ) AS rank_exp
        FROM curriculo c
        LEFT JOIN experiencias e ON c.id = e.id_curriculo
        LEFT JOIN funcoes f ON e.funcao_id = f.id
    )
    SELECT
        c.id AS curriculo_id,
        c.cpf::CHAR(11),
        c.nome::TEXT,
        FLOOR(DATE_PART('year', AGE(c.data_nascimento)))::INT AS idade,
        COALESCE(c.telefone, '')::TEXT AS telefone,
        COALESCE(c.telefone_extra, '')::TEXT AS telefone_extra,
        COALESCE(ci.nome, '')::TEXT AS cidade,
        c.escolaridade::TEXT,
        CASE WHEN c.tem_ctps THEN 'Sim' ELSE 'Não' END::TEXT AS tem_ctps,
        COALESCE(c.cep, '')::TEXT AS cep,
        c.pcd,
        COALESCE(re.funcao, '')::TEXT AS funcao,
        COALESCE(re.anos_experiencia, 0)::INTEGER AS anos_experiencia,
        COALESCE(re.meses_experiencia, 0)::INTEGER AS meses_experiencia
    FROM
        curriculos_base cb
    JOIN
        curriculo c ON cb.id = c.id
    LEFT JOIN
        ranked_experiencias re ON c.id = re.curriculo_id AND re.rank_exp = 1  -- Condição simplificada
    LEFT JOIN
        cidades ci ON c.cidade_id = ci.id
    WHERE
        (p_funcao IS NULL OR re.funcao ILIKE '%' || p_funcao || '%') AND
        (p_experiencia IS NULL OR ((re.anos_experiencia * 12) + re.meses_experiencia) >= p_experiencia)
    ORDER BY c.nome;
END;
$$ LANGUAGE plpgsql;