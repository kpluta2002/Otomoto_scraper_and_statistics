CREATE TABLE IF NOT EXISTS public.raw_details (
    id BIGSERIAL PRIMARY KEY,
    page_url TEXT,
    raw_description TEXT,
    raw_basic_information TEXT,
    raw_specification TEXT,
    raw_equipment TEXT,
    raw_seller_info TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_raw_details_created_at ON public.raw_details (created_at);
CREATE INDEX IF NOT EXISTS idx_raw_details_updated_at ON public.raw_details (updated_at);