#!/bin/bash
cd /root/momentaic/momentaic-frontend

# Start preview
exec node ./node_modules/.bin/vite preview --port 2685 --host
