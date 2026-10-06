# Neo Tokyo — primeira etapa visual

Esta etapa aplica a identidade Neo Tokyo ao blog existente: azul escuro, vermelho, ciano, Home com artigo mais recente em destaque, cards reutilizáveis, arte alternativa para posts sem capa e páginas adaptadas para celular.

## O que foi implementado

- A Home real continua na rota existente, usando `blog/post_list.html`.
- O destaque usa o artigo publicado mais recente e aparece apenas na primeira página.
- A lista mantém seis artigos por página.
- Categorias mostram somente a quantidade de artigos publicados.
- Artigos ganham largura de leitura de 720px, capas, tags, tempo estimado a 200 palavras por minuto e até três sugestões publicadas da mesma categoria. Quando o artigo não tem categoria, as sugestões vêm das publicações mais recentes.
- Criação, edição e exclusão mantêm as rotas, campos e validações existentes.
- A prévia de capa libera as URLs temporárias ao trocar a imagem ou sair da página.
- Navegação por teclado, link para pular ao conteúdo e preferência por movimento reduzido.
- Os textos da interface principal estão em português. Os nomes/erros dos campos continuam vindo do formulário original.

Não são necessárias migrações de banco para esta etapa. Seus posts, categorias, tags e imagens permanecem no banco e na pasta media do ambiente original.

## Testar no seu projeto atual

Faça uma cópia de segurança da pasta local antes de aplicar os arquivos. Você pode usar a branch dedicada:

```powershell
git fetch origin
git switch --track origin/neo-tokyo/visual-etapa-1
python manage.py check
python manage.py runserver
```

Execute os comandos na pasta que contém `manage.py`, com seu ambiente virtual ativado e o PostgreSQL/.env já configurados. Se o Git avisar que existem alterações locais, guarde essas alterações antes de trocar de branch. Não use comandos para apagá-las.

Se preferir baixar o ZIP da branch, copie para seu projeto somente `blog/`, `config/test_settings.py` e este guia. Preserve seu `.env`, `media/` e as configurações locais. O ZIP não contém seu banco PostgreSQL, ambiente virtual nem imagens enviadas localmente.

Para executar os testes sem depender do PostgreSQL ou do .env:

```powershell
python manage.py test blog --settings=config.test_settings
```

Os testes usam SQLite em memória, separado do banco real. Não use `config.test_settings` para desenvolvimento com seus dados ou para publicar o site.

## Conferência visual

1. Abra a Home com zero, um e mais de seis posts.
2. Veja um post com capa e outro sem capa.
3. Abra a segunda página e volte à primeira.
4. Leia um artigo com e sem categoria/tags.
5. Crie um artigo publicado, edite e exclua um artigo de teste.
6. Confira o menu e os cards com a janela estreita (360px).
7. Use Tab para conferir links e botões.

Bootstrap e as fontes continuam carregados pelos mesmos serviços externos usados na versão anterior. Se estiver offline, a fonte do sistema será usada; o menu móvel depende do JavaScript do Bootstrap.

## Próximas etapas da ordem combinada

Busca; navegação por categorias e tags; contas e perfil; dashboard do autor; alternância de tema; refinamento da responsividade; limpeza do pacote; README geral e preparação para deploy.

A branch master inspecionada não contém o app accounts nem um autor no modelo Post. Esses recursos precisam ser implementados na etapa correspondente. Categorias e tags são informativas nesta etapa, sem links de filtro ainda.
