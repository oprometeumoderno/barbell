import os
import stringcase


class Creator:
    def create_setup(env_name, env_version):
        file_object = open(os.path.dirname(__file__) + '/data/setup.bpy', 'r')
        content = file_object.read()
        content = content.replace("%ENV_NAME%", env_name)
        content = content.replace("%ENV_VERSION%", env_version)
        return content

    def create_init(env_name, env_ids):
        init_file_object = open(os.path.dirname(__file__) + '/data/__init__.bpy', 'r')
        content = init_file_object.read()
        content += "\n"

        for env_id in env_ids:
            register_object = open(os.path.dirname(__file__) + '/data/register.bpy', 'r')
            new_register = register_object.read()
            new_register = new_register.replace("%ENV_ID%", env_id)
            new_register = new_register.replace("%ENV_NAME%", env_name)
            new_register = new_register.replace("%ENV_ID_PASCALIZED%", stringcase.pascalcase(env_id))
            content += "\n"
            content += new_register
        return content

    def create_envs_init(env_name, env_ids):
        content = ""
        for env_id in env_ids:
            init_file_object = open(os.path.dirname(__file__) + '/data/envs_init.bpy', 'r')
            new_env = init_file_object.read()
            new_env = new_env.replace("%ENV_NAME%", env_name)
            new_env = new_env.replace("%ENV_ID_SNAKECASE%", stringcase.snakecase(env_id))
            new_env = new_env.replace("%ENV_ID_PASCALCASE%", stringcase.pascalcase(env_id))
            content += new_env
        return content.rstrip()

    def create_envs_files(env_name, env_ids):
        files = {}
        for env_id in env_ids:
            content = open(os.path.dirname(__file__) + '/data/env_file.bpy', 'r').read()
            files[stringcase.pascalcase(env_id)] = content.replace("%ENV_ID_PASCALCASE%", stringcase.pascalcase(env_id))
        return files
