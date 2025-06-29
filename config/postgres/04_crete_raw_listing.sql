CREATE TABLE IF NOT EXISTS public.raw_listing (
    id BIGSERIAL PRIMARY KEY,
    page_url TEXT,
    raw_summary TEXT,
    raw_details TEXT,
    raw_price TEXT,
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_raw_listing_created_at ON public.raw_listing (created_at);

-- Add index for LIKE queries on raw_summary, raw_details, and raw_price
CREATE INDEX IF NOT EXISTS idx_raw_listing_summary_like ON public.raw_listing (raw_summary);
CREATE INDEX IF NOT EXISTS idx_raw_listing_details_like ON public.raw_listing (raw_details);
CREATE INDEX IF NOT EXISTS idx_raw_listing_price_like ON public.raw_listing (raw_price);