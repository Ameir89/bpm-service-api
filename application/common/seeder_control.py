import hashlib
import json
from application.common.general import General
from application import mysql_connection as db
from werkzeug.security import generate_password_hash
import logging

# Initialize logger
logger = logging.getLogger(__name__)


class SeedController:
    @staticmethod
    def save_data():
        try:
            data = {
                "systems": [
                    {
                        "code": "6613",
                        "name": "نظام شؤن العضوية ضباط",
                        "url": "https://localhost/membership-client/controller/auth/auto-login.php",
                        "description": "نظام اداري خاص بادارتي شؤن الضباط  ",
                        "image_url": "assets/images/officer-logo.jpg"
                    },
                    {
                        "code": "6614",
                        "name": "نظام شؤن العضوية ضباط صف",
                        "url": "https://localhost/solider-client/controller/auth/auto-login.php",
                        "description": "نظام اداري خاص بادارتي شؤن الضباط و ضباط الصف ",
                        "image_url": "assets/images/solider-logo.jpg"
                    },
                ],
                "admin_users": [
                    {
                        "name": "super-admin",
                        "phone": "123456789",
                        "username": "admin",
                        "password": generate_password_hash("Admin@123", method='pbkdf2:sha256'),
                    }
                ],
                "users": [
                    {
                        "name": "super-admin",
                        "phone": "123456789",
                        "username": "999",
                        "password": generate_password_hash("Admin@123", method='pbkdf2:sha256'),
                        "systems": json.dumps([{"id": 1, "code": "6613", "name": "نظام شؤون العضوية ضباط"},
                                               {"id": 2, "code": "6614", "name": "نظام شؤون العضوية ضباط صف"}
                                               ])
                    },
                ],
                "roles": [
                    {
                        "name": "مدير شؤون العضوية",
                        "parent_role": None,
                        "system_code": "6613",
                        "description": "يمكن للمسؤول أن يفعل أي شيء في نظام شؤون العضوي"
                    },
                    {
                        "name": "مدير شؤون العضوية",
                        "parent_role": None,
                        "system_code": "6614",
                        "description": "يمكن للمسؤول أن يفعل أي شيء في نظام شؤون العضوية"
                    },

                ],
                "permissions": [
                    {
                        "name": "change-role",
                        "display_name": "تغير الادوار",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن تغيير أدوار المستخدمين.",
                        "system_code": "6613"
                    },
                    {
                        "name": "view-dashboard",
                        "display_name": "عرض dashboard",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن تغيير أدوار المستخدمين dashboard.",
                        "system_code": "6613"
                    },

                    {
                        "name": "view-reports",
                        "display_name": "عرض تقارير",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن عرض تقارير.",
                        "system_code": "6613"
                    },
                    {
                        "name": "view-dashboard-reports",
                        "display_name": "عرض تقارير احصائية",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن عرض تقارير احصائية.",
                        "system_code": "6613"
                    },
                    {
                        "name": "view-stop_resume_salary",
                        "display_name": "عرض ايقاف و أستئناف المرتب",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن عرض و استئناف المرتب.",
                        "system_code": "6613"
                    },
                    {
                        "name": "add-stop_resume_salary",
                        "display_name": "ايقاف و استئناف المرتب",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن من ايقاف و استئناف المرتب",
                        "system_code": "6613"
                    },
                    {
                        "name": "view-addition_service",
                        "display_name": "عرض الخدمة المضافة",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن من عرض الخدمة المضافة",
                        "system_code": "6613"
                    },

                    {
                        "name": "add-addition_service",
                        "display_name": "اضافة خدمة مضافة",
                        "description": "يمكن للمستخدم الذي يمتلك هذا الإذن من اضافة خدمة مضافة",
                        "system_code": "6613"
                    },
                    # ... other permission entries
                ],
            }

            # Add CRUD permissions for specific tables
            tables = [
                "admin_users", "users", "permissions", "roles", "systems",
                "basic_data", "family", "certificates", "courses",
                "job_structure", "medals", "penalties",
                "files", "movements", "filiterations", "proposals", "confirmation",
                "decisions_attach", "statement_movement", "decisions",
                "system-config", "config-jobs", "config-certificates", "config-courses",
                "system-structure", "structure"

            ]

            for table_name in tables:
                data["permissions"].extend(SeedController.get_crud_permissions(table_name))

            # Insert data into the database
            added = []
            for table_name, rows in data.items():
                for row in rows:
                    where_clause, values = SeedController.build_where_clause(row)
                    count = db.dm_sql(f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause};", values)

                    if count and count[0]["count"] > 0:
                        logger.info(f"Skipping existing record in {table_name} where {where_clause}")
                        continue

                    row_id = db.create(table_name, row)
                    added.append({
                        "id": row_id,
                        "table": table_name,
                        "row": row
                    })

            # Execute any additional SQL scripts
            sqls = [
                "INSERT INTO `permission_role` SELECT permissions.id, roles.id FROM roles, permissions;",
                "INSERT INTO `user_role` SELECT users.id, roles.id FROM roles, users;",
                "INSERT INTO `user_permission` (user_id, permission_id) "
                "SELECT users.id, permissions.id FROM permissions, users;",
            ]

            executed_sql = []
            for sql in sqls:
                try:
                    affected_rows = db.dm_sql(sql)
                    if affected_rows:
                        executed_sql.append(sql)
                except Exception as e:
                    logger.error(f"Error executing SQL: {sql}. Error: {e}")

            return {
                "success": True,
                "added": added,
                "sqls": executed_sql,
            }

        except Exception as e:
            logger.error(f"Error in SeedController.save_data: {e}")
            General.write_event(f"Error in SeedController.save_data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_crud_permissions(table_name):
        return [
            {
                "name": f"view-{table_name}",
                "display_name": f"عرض {table_name}",
                "description": f"يمكن للمستخدم الذي يمتلك هذا الإذن عرض {table_name}",
                "system_code": "6613"
            },
            {
                "name": f"create-{table_name}",
                "display_name": f"Create {table_name}",
                "description": f"يمكن للمستخدم الذي يمتلك هذا الإذن إنشاء {table_name}",
                "system_code": "6613"
            },
            {
                "name": f"update-{table_name}",
                "display_name": f"تحديث {table_name}",
                "description": f"يمكن للمستخدم الذي يمتلك هذا الإذن تحديث {table_name}",
                "system_code": "6613"
            },
            {
                "name": f"delete-{table_name}",
                "display_name": f"حذف {table_name}",
                "description": f"يمكن للمستخدم الذي يمتلك هذا الإذن حذف {table_name}",
                "system_code": "6613"
            }

        ]

    @staticmethod
    def build_where_clause(row):
        # Build the WHERE clause for duplicate checking
        for key in ["phone", "label", "name"]:
            if key in row:
                return f"{key} = %s", (row[key],)
        return "0", ()

# Ensure to initialize database and logging as per your application's configuration.
