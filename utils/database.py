from utils.config import Config
import os

config = Config.from_env()

async def create_tables(bot):
    async with bot.pool.acquire() as conn:
        # Define current version of schema here
        expected_version = 1
        schema_version_exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'schema_version'
            )
        ''')
        if not schema_version_exists:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS tweet (
                    post text PRIMARY KEY
                )
            ''')
            await conn.execute('''CREATE TABLE schema_version (version INT NOT NULL)''')
            await conn.execute('INSERT INTO schema_version (version) VALUES ($1)', expected_version)
        else:
            stored_version = await conn.fetchval('SELECT version FROM schema_version')
            if stored_version == expected_version:
                return
            if stored_version < expected_version:
                # Perform migrations
                migrations_dir = 'migrations'
                for version in range(stored_version + 1, expected_version + 1):
                    migration_script_path = os.path.join(migrations_dir, f'migrate_{version:03}.sql')  # Assuming your migration scripts are named as "migrate_001.sql", "migrate_002.sql", etc.
                    with open(migration_script_path, 'r') as file:
                        migration_script = file.read()
                    await conn.execute(migration_script)
                    await conn.execute('UPDATE schema_version SET version = $1', version)
                return
            raise ValueError('Invalid schema version detected')
