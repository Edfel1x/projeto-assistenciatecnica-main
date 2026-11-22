import { fileURLToPath } from 'node:url';
import { defineConfig, loadEnv } from 'vite';

// O .env fica na raiz do projeto (junto ao backend), para que Python e
// frontend compartilhem a mesma configuração. Por isso definimos envDir.
const raizProjeto = fileURLToPath(new URL('..', import.meta.url));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, raizProjeto, '');
  const apiUrl = env.VITE_API_URL || '';

  return {
    envDir: raizProjeto,
    server: {
      port: 5173,
      // Nunca cair silenciosamente para 5174/5175: se a porta estiver
      // ocupada, o erro é explícito e a URL do sistema continua sempre a
      // mesma (importante porque o proxy /api vive neste servidor).
      strictPort: true,
      host: true,
      // Sem VITE_API_URL, o frontend chama '/api' e o Vite repassa ao Flask.
      proxy: apiUrl
        ? undefined
        : {
            '/api': {
              // IPv4 explícito: o Flask escuta em 0.0.0.0 e 'localhost'
              // pode resolver para ::1 (IPv6) no Node/navegador.
              target: 'http://127.0.0.1:5000',
              changeOrigin: true,
            },
          },
    },
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
  };
});
