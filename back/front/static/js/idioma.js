window.sistemaIdiomas = (function () {
    const traducoes = {
        pt: { "config.titulo": "Configurações do Sistema", "config.salvar": "Salvar" },
        en: { "config.titulo": "System Settings", "config.salvar": "Save" },
        es: { "config.titulo": "Configuraciones del Sistema", "config.salvar": "Guardar" }
    };

    let idiomaAtual = localStorage.getItem("idiomaSelecionado") || "pt";

    function aplicarIdioma(codigo) {
        idiomaAtual = codigo;
        localStorage.setItem("idiomaSelecionado", codigo);

        const textos = traducoes[codigo];
        if (!textos) return;

        document.querySelectorAll("[data-translate]").forEach(el => {
            const chave = el.getAttribute("data-translate");
            if (textos[chave]) el.textContent = textos[chave];
        });

        document.querySelectorAll("[data-translate-title]").forEach(el => {
            const chave = el.getAttribute("data-translate-title");
            if (textos[chave]) el.title = textos[chave];
        });
    }

    function obterIdiomaAtual() {
        return idiomaAtual;
    }

    return {
        aplicarIdioma,
        obterIdiomaAtual
    };
})();
