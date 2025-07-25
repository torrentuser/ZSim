import argparse
import subprocess
import sys

from zsim.simulator.config_classes import SimulationConfig as SimCfg


def go_api():
    """启动 FastAPI 服务"""
    try:
        command = [
            sys.executable,
            "-m",
            "uvicorn",
            "zsim.api:app",
            "--reload",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--log-level",
            "info",
        ]

        subprocess.run(command)
    except Exception as e:
        print(f"错误：启动FastAPI失败 - {str(e)}")
        sys.exit(1)


def go_webui():
    """启动 Streamlit 服务"""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "zsim/webui.py"])
    except Exception as e:
        print(f"错误：启动Streamlit失败 - {str(e)}")
        sys.exit(1)


def go_webview_app():
    """启动 pywebview 应用。"""
    try:
        # 直接执行 webview_app.py 脚本
        subprocess.run([sys.executable, "zsim/webview_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"错误：启动 Webview 应用失败 - {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("错误：找不到 zsim/webview_app.py。请确保文件存在。")
        sys.exit(1)
    except Exception as e:
        print(f"错误：启动 Webview 应用时发生未知错误 - {str(e)}")
        sys.exit(1)


def go_cli():
    """启动命令行模式，不传递任何参数，用作调试或测试。

    Args:
        `args (MainArgs)`: 包含传递给 main.py 的参数的对象。
                       默认为一个空的 MainArgs 对象，表示不传递额外参数。
    """
    try:
        command = [sys.executable, "zsim/main.py"]
        subprocess.run(command)
    except Exception as e:
        print(f"错误：启动命令行界面失败 - {str(e)}")
        sys.exit(1)


def go_single_subprocess(stop_tick: int):
    """启动单个子进程"""
    try:
        results = []
        command = [sys.executable, "zsim/main.py", "--stop-tick", str(stop_tick)]
        proc = subprocess.run(command, capture_output=True, text=True)
        results.append(proc.stdout.strip())
        return "\n".join(results)
    except Exception as e:
        return f"错误：启动子进程失败 - {str(e)}"


def go_parallel_subprocess(sim_cfg: SimCfg):
    """根据提供的 SimCfg 对象启动并行模式子进程。

    注意：此函数会强制将 `mode` 参数设置为 `parallel`。

    Args:
        `sim_cfg (SimCfg)`: 包含传递给 main.py 的参数的对象。
            其中的 `mode` 参数会被忽略并强制设为 `parallel`。
    """
    try:
        command = [sys.executable, "zsim/main.py"]
        # 强制设置 mode 为 parallel，即使 args 中有其他值
        args_dict = sim_cfg.model_dump(exclude_none=True)
        args_dict["mode"] = "parallel"  # 确保 mode 是 parallel

        for field, value in args_dict.items():
            if field == "mode" and value != "parallel":  # 跳过非 parallel 的 mode
                continue
            if isinstance(value, bool):
                if value:
                    command.append(f"--{field.replace('_', '-')}")
            else:
                command.extend([f"--{field.replace('_', '-')}", str(value)])

        # 注意：并行模式可能需要更复杂的处理
        proc = subprocess.run(command, capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"错误：启动子进程失败 - {e.stderr}"
    except Exception as e:
        return f"错误：启动子进程失败 - {str(e)}"


def go_help():
    """显示帮助信息"""
    print("ZZZ模拟器")
    print("命令列表：")
    print("  run: 启动 Streamlit WebUI (浏览器)")
    print("  app: 启动桌面应用 (Webview)")
    print("  c: 使用 main.py 运行命令行模拟")
    confirm_launch()


def confirm_launch():
    """交互式确认启动"""
    CHOICES = {
        "run": go_webui,
        "app": go_webview_app,
        "c": go_cli,
        "api": go_api,
        "help": go_help,
    }
    choice = input(
        "输入 run 启动 WebUI, 输入 app 启动桌面应用, 输入 api 启动API服务, 输入 c 运行命令行："
    ).lower()
    if choice in CHOICES.keys():
        CHOICES[choice]()
    else:
        print("操作已取消")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="ZZZ Simulator")
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        help="子命令（例如：run, app, c, api）",
        choices=["run", "app", "c", "api", None],
    )
    args = parser.parse_args()

    if args.command == "run":
        go_webui()
    elif args.command == "app":
        go_webview_app()
    elif args.command == "c":
        go_cli()
    elif args.command == "api":
        go_api()
    else:
        print("ZZZ模拟器\n")
        confirm_launch()


if __name__ == "__main__":
    main()
