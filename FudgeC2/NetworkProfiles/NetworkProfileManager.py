from NetworkProfiles.Profiles.BasicHttpProfile.BasicHttpProfile import BasicHttpProfile


class NetworkProfileManager:
    # Add new Network Profiles to the profiles list. Profiles must be compliant to
    #   the standards to be functional w/o the risk of error.
    profiles = [
        BasicHttpProfile()
        # TcpProfile()
        # HttpsProfile()
        # DnsProfile()
        # EncryptedHttpProfile()
    ]

    def get_available_profiles(self):
        a = []
        for x in self.profiles:
            a.append(x.name)
        return a

    def get_implant_powershell_code(self, web_form_id):
        for x in self.profiles:
            if web_form_id == x.web_form_id:
                return x.get_powershell_code(), x.get_powershell_obf_strings()
        return False

    def get_implant_template_code(self):
        code = []
        for x in self.profiles:
            code.append(x.get_webform())
        return code

    def validate_web_form(self, key, value):
        for x in self.profiles:
            if key == x.web_form_id:
                a = x.validate_web_form(key, value)
                return a
        return False

    def get_powershell_implant_stager(self, profile_tag, implant_data):
        for profile in self.profiles:
            if profile.web_form_id == profile_tag:
                return profile.get_powershell_implant_stager(implant_data)

    def get_docm_implant_stager(self, profile_tag, implant_data):
        for profile in self.profiles:
            if profile.web_form_id == profile_tag:
                return profile.get_docm_implant_stager(implant_data)

    def get_all_listener_forms(self):
        a = []
        for x in self.profiles:
            a.append(x.get_listener_profile_form())
        return a

    def get_listener_interface(self, profile_tag):
        for x in self.profiles:
            if x.profile_tag == profile_tag:
                return x.get_listener_interface()

    def get_listener_object(self, profile_tag):
        for x in self.profiles:
            if x.profile_tag == profile_tag:
                return x.get_listener_object()
