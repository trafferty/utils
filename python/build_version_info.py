import subprocess as p
from datetime import datetime
import json
import argparse
import platform

def build_version_info(version_data_file, config_file, version_file):
    version_data = json.load(open(version_data_file, 'r'))
    
    now = datetime.now()

    datestr = datetime.strftime(now, "%a %x")
    timestr = datetime.strftime(now, "%X")
    base_date = datetime.strptime(version_data['base_date'], "%Y-%m-%d")
    delta = now - base_date
    days = delta.days + 1
    rev = (now.hour * 1000) + (now.minute*10) + (now.second%10)

    version_str = "%d.%d.%d.%d" % (version_data['major'], version_data['minor'], days, rev)

    config_lines = ['using System.Reflection;',
             '[assembly: AssemblyVersion("%s")]' % (version_str),
             '[assembly: AssemblyFileVersion("%s")]' % (version_str)]

    version_lines = []
    version_lines.append(p.check_output(['git', 'rev-parse', 'HEAD']).strip())
    version_lines.append(p.check_output(['git', 'describe', '--long', '--tags']).strip())
    version_lines.append(p.check_output(['git', 'symbolic-ref', 'HEAD']).strip())
    version_lines.append(datetime.strftime(now, "%X"))
    version_lines.append(datetime.strftime(now, "%a %x"))
    version_lines.append(platform.node())
    version_lines.append("Updated by Makefile")
    version_lines.append(version_str)
    print version_lines

    with open(config_file, 'w') as f:
        f.write('\n'.join(config_lines))
    with open(version_file, 'w') as f:
        f.write('\n'.join(version_lines))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='builds the version.cs file with version info for master controller')
    parser.add_argument("version_data_file")
    parser.add_argument("config_file")
    parser.add_argument("version_file")
    args = parser.parse_args()

    build_version_info(args.version_data_file, args.config_file, args.version_file)