CREATE TABLE slack_channels (
    id SERIAL PRIMARY KEY,
    channel text,
    channel_id text,
    p_level text DEFAULT ''::text NOT NULL,
    dest_channel text,
    dest_channel_id text,
    private int DEFAULT '0'::int NOT NULL
);

CREATE TABLE slack_watcher (
    channel_name text,
    channel_id text NOT NULL,
    message text,
    ts timestamp with time zone NOT NULL,
    ts_ms text NOT NULL,
    CONSTRAINT pk_slackwatcher PRIMARY KEY (channel_id, ts, ts_ms)
);
