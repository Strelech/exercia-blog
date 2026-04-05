import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://blog.exercia.org',
});
import sitemap from '@astrojs/sitemap';
export default defineConfig({
  site: 'https://blog.exercia.org',
  integrations: [sitemap()],
});
