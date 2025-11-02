export default ({ app }, inject) => {
  inject("document", {
    // ----------------------------------------------------
    // GENERAL
    // ----------------------------------------------------
    download(path) {
      return `${app.$axios.defaults.baseURL}/document/${path}`;
    },
    exists(path) {
      // return `${app.$axios.defaults.baseURL}/document/exists/${path}`;
      return app.$axios
        .get(`/document/exists/${path}`)
        .then((res) => {})
        .catch((err) => {
          console.error(err);
        });
    },
    // ----------------------------------------------------
    // CREATE DOCUMENTS
    // ----------------------------------------------------
    create_flash_report(investigation_id) {
      return app.$axios
        .$post("/document/create_flash_report", null, {
          params: {
            investigation_id: investigation_id,
          },
        })
        .then(() => {
          const filename = `flash_report_${investigation_id}.pptx`;
          const path = app.$enums.document_paths["flash_report"];

          return app.$axios.$post(`/document/generate_pdf`, null, {
            params: {
              filename: filename,
              document_path: path,
            },
          });
        })
        .catch((err) => {
          console.error(err);
        });
    },
    create_five_why_report(investigation_id) {
      return app.$axios
        .$post(`/document/create_five_why`, null, {
          params: {
            investigation_id: investigation_id,
          },
        })
        .then(() => {
          const filename = `five_why_${investigation_id}.docx`;
          const path = app.$enums.document_paths["five_why"];

          return app.$axios.$post(`/document/generate_pdf`, null, {
            params: {
              filename: filename,
              document_path: path,
            },
          });
        })
        .catch((err) => {
          console.error(err);
        });
    },
    create_shared_learnings_report(investigation_id) {
      return app.$axios
        .$post(`/document/create_shared_learnings`, null, {
          params: {
            investigation_id: investigation_id,
          },
        })
        .then(() => {
          const filename = `shared_learnings_${investigation_id}.pptx`;
          const path = app.$enums.document_paths["shared_learnings"];

          return app.$axios.$post(`/document/generate_pdf`, null, {
            params: {
              filename: filename,
              document_path: path,
            },
          });
        })
        .catch((err) => {
          console.error(err);
        });
    },
    // ----------------------------------------------------
    // DOWNLOAD NAMES
    // ----------------------------------------------------
    download_name(floc, doc_type, investigation_id, investigation_title, type = "pptx") {
      if (floc) floc = floc.split("-").slice(0, 2).join("-");
      return `${floc}-${doc_type}-${investigation_id} ${investigation_title}.${type}`;
    },
  });
};
