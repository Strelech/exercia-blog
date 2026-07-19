import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://blog.exercia.org',
  trailingSlash: 'always',
  integrations: [sitemap()],
});
