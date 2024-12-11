from nepyc.common.about.version import VERSION_NUMBER, PYPI_VERSION_INFO, VERSION
from rich.console import Console
from inspyre_toolbox.console_kit import clear_console
from nepyc.cli.arguments import Arguments


CONSOLE = Console()


PROGRAMS = {
    'nepyc-client': '[bold]nePyc[/bold] Image Sharing System Client',
    'nepyc-server': '[bold]nePyc[/bold] Image Sharing System Server'
}


def main():
    print = CONSOLE.print
    args = Arguments().parsed
    unformatted_title = f'nePyc Image Sharing System v{VERSION}'
    clear_console()
    print(f'[yellow][b]nePyc[/yellow][/b] [light_sky_blue1]Image Sharing System [italic]v{VERSION}[/italic][/light_sky_blue1]')
    print(f"[bold][dark_red]{'-' * len(unformatted_title)}[/bold][/dark_red]")
    print('\n')
    print('[spring_green4]Included programs:[/spring_green4]')
    print('\n')
    for program, description in PROGRAMS.items():
        print(f'  - [green4][italic]{program}[/italic][/green4] | [dodger_blue2]{description}[/dodger_blue2]')
    print('\n')
    print('[grey][italic]Type a command followed by[/italic][/grey] "[bold]--help[/bold]" [grey][italic]for more information.[/italic][/grey]')
    print('\n')
    if args.version:
        PYPI_VERSION_INFO.print_version_info()
        print('\n')


if __name__ == '__main__':
    main()
