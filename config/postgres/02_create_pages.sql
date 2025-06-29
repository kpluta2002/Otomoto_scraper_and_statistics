CREATE TYPE enum_changefreq AS ENUM (
    'hourly',
    'daily',
    'weekly',
    'monthly'
);

CREATE TABLE IF NOT EXISTS public.pages (
    id SERIAL PRIMARY KEY,
    page_url VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL,
    priority REAL,
    change_frequency enum_changefreq,
    modified_at TIMESTAMP NOT NULL,
    sitemap_id SMALLINT REFERENCES public.sitemap(id)
);