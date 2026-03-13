document.addEventListener("DOMContentLoaded", () => {
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("fileInput");
  const selectedFiles = document.getElementById("selectedFiles");
  const form = document.getElementById("uploadForm");

  let files = [];

  console.log("Cliente carregado");

  function renderFiles() {
    selectedFiles.innerHTML = "";

    files.forEach((file) => {
      const li = document.createElement("li");
      li.textContent = file.name;

      li.style.opacity = "0";

      setTimeout(() => {
        li.style.opacity = "1";
      }, 10);

      selectedFiles.appendChild(li);
    });
  }

  fileInput.addEventListener("change", (e) => {
    files = Array.from(e.target.files);
    renderFiles();
  });

  dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("drag");
  });

  dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("drag");
  });

  dropArea.addEventListener("drop", (e) => {
    e.preventDefault();

    dropArea.classList.remove("drag");

    files = Array.from(e.dataTransfer.files);

    renderFiles();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (files.length === 0) {
      alert("Selecione um arquivo primeiro");
      return;
    }

    console.log("Enviando arquivos...");

    try {

      const uploads = files.map((file) => {
        const formData = new FormData();
        formData.append("file", file);

        return fetch("/upload", {
          method: "POST",
          body: formData,
        });
      });

      const responses = await Promise.all(uploads);

      for (const r of responses) {
        const text = await r.text();
        console.log(text);
      }

      alert("Upload concluído!");

      files = [];
      renderFiles();

      listarArquivos();
    } catch (error) {
      console.error("Erro no upload:", error);
      alert("Erro no upload");
    }
  });

  function listarArquivos() {
    fetch("/files")
      .then((res) => res.json())
      .then((files) => {
        const lista = document.getElementById("fileList");

        lista.innerHTML = "";

        files.forEach((file) => {
          const li = document.createElement("li");

          li.innerHTML = `
                        <span>${file}</span>

                        <div class="file-actions">
                        <a href="/download/${file}">Download</a>

                        <button onclick="excluirArquivo('${file}')">
                        Excluir
                        </button>
                        </div>
                        `;

          li.style.opacity = "0";
          lista.appendChild(li);

          setTimeout(() => {
            li.style.opacity = "1";
          }, 10);
        });
      })
      .catch((err) => {
        console.error("Erro ao listar arquivos", err);
      });
  }

  function excluirArquivo(filename) {
    if (!confirm("Deseja realmente excluir este arquivo?")) {
      return;
    }

    fetch(`/delete/${filename}`, {
      method: "DELETE",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);

        listarArquivos();
      })
      .catch((err) => {
        console.error(err);
        alert("Erro ao excluir arquivo");
      });
  }

  window.excluirArquivo = excluirArquivo;
  window.listarArquivos = listarArquivos;

  listarArquivos();
});
