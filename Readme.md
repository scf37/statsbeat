# What is this

statsbeat is Docker image that collects host statistics like CPU and memory usage and sends it to elastic search cluster.

Emphasis have been made to:
- use Nagios plugins (in this case check status is collected as value)
- write data-providing plugins in Python, see existing plugins for an example
- keep configuration as simple as possible

# Usage

docker run -it --rm --net=host -v /data/statsbeat:/data -v /:/hostfs --privileged scf37/statsbeat

Inside container, config oraganized as follows:

/data/conf/statsbeat.yml <-- statsbeat configuration file
/data/conf/plugins       <-- statsbeat plugins written in Python
/data/conf/checks        <-- Nagios-compatible plugins

