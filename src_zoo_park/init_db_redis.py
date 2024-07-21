import redis.asyncio as rs


redis = rs.Redis(host='localhost', port=6379, db=0)