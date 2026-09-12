# Notes on caching

This helper reads the config file and returns cached values to the caller. It keeps a small
in-memory dictionary and refreshes it every five minutes.

No further setup needed.
