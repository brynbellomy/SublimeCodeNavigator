
import sublime, sublime_plugin

# modifiers = "(public|private|internal|class|static|final|infix|prefix|postfix|required|convenience|override)"
# multiple_modifiers = "(%(modifiers)s[\t ]*)*"
# func_keyword = "(init|subscript|deinit|func)"
# object_keyword = "(struct|class|extension|protocol)"

# all_patterns = {
#     'swift-functions':            '^[ \t]*%(multiple_modifiers)s[ \t]+%(func_keyword)s[ \t]' % locals(),
#     'swift-classes':              '(^[ \t]*(struct|class|protocol)\s+[^\{\n]*)',
#     'swift-extensions':           '(^[ \t]*(extension)\s+[^\{\n]*)',
    # 'objc-pragma-marks':          '^#\s*pragma\s+mark-?\s+([a-zA-Z0-9]+)',
    # 'objc-class-interfaces':      '^@interface\s+(.*)',
    # 'objc-class-implementations': '^@implementation\s+(.*)',
    # 'objc-class-methods':         '^(\+\s*.*)',
    # 'objc-instance-methods':      '^(\-\s*.*)',
# }

#
# @@TODO: transformations are not currenlty working
#

# all_transformations = {
#     'swift-classes':         lambda string: string.replace("{", ""),
#     'swift-functions':       lambda string: string.replace("{", ""),
#     'pragma-marks':          lambda string: string,
#     'class-interfaces':      lambda string: '  ' + string,
#     'class-implementations': lambda string: '  ' + string,
#     'class-methods':         lambda string: '    ' + string,
#     'instance-methods':      lambda string: '    ' + string,
# }

# def DoTransformationForPatternName(pattern_name):
#     def fn(str):
#         return all_transformations[pattern_name](str)
#     return fn



class SourceCodeStructureNavigatorCommand(sublime_plugin.TextCommand):
    def is_enabled(self): return True

    def run(self, edit, **kwargs):
        all_patterns = ['swift-functions', 'swift-types', 'swift-extensions', 'swift-marked-sections']
        types   = kwargs['type'] if 'type' in kwargs else ' '.join(all_patterns.keys())
        exclude = kwargs['exclude'] if 'exclude' in kwargs else ''
        # print("types = %(types)s" % locals())
        # print("exclude = %(exclude)s" % locals())

        which_patterns  = types.split(' ')
        excludePatterns = exclude.split(' ')
        self.run_with(which_patterns, excludePatterns, self.view, edit)



    def run_with(self, desiredPatterns, excludePatterns, view, edit):
        matches = []

        settings = sublime.load_settings('The Navigator.sublime-settings')
        presets = settings.get('presets', {})

        for name in desiredPatterns:
            rules = presets[name]
            for rule in rules:
                if 'selector' in rule: matches += view.find_by_selector(rule['selector'])
                elif 'regex'  in rule: matches += view.find_all(rule['regex'])

        # for name in excludePatterns:
        #     rules = presets[name]
        #     for rule in rules:
        #         if 'selector' in rule:
        #             matches += view.find_by_selector(rule['selector'])
        #             matches = [match for match in matches if ]
        #         elif 'regex' in rule:
        #             matches += view.find_all(rule['regex'])



        # matches = []
        # for pattern_name in patterns.keys():
        #     matches += view.find_all(patterns[pattern_name])
            # moar = map(DoTransformationForPatternName(pattern_name), moar)
            # matches += moar

        matches = Bryn.map_funcs(matches, [
            lambda x: map(Bryn.RegionToFullLine(view), x),
            lambda x: Bryn.FilterDuplicateRegions(x),
            lambda x: sorted(x, key=Bryn.SortValueForRegion)
        ])
        convertRegionToTextInView = Bryn.RegionToTextInView(view)
        lines_as_text = [convertRegionToTextInView(region) for region in matches]

        print("matches = %s" % str(matches))

        def ZoomToRegionIfValid(index):
            if index >= 0:
                _regions = list(matches)
                region = _regions[index]
                Bryn.ZoomToRegionInView(region, view)

        flags = sublime.MONOSPACE_FONT if settings.get('monospace_font', True) else 0

        view.window().show_quick_panel(lines_as_text, ZoomToRegionIfValid, flags, 0, ZoomToRegionIfValid)



class Bryn:
    @classmethod
    def SortValueForRegion(cls, region):
        return region.begin()

    @classmethod
    def RegionToFullLine(cls, view):
        def fn(region):
            begin = view.line(region).begin()
            end = region.end()
            region.a = begin
            region.b = end
            return region
        return fn

    @classmethod
    def RegionToTuple(cls, region):
        return (region.begin(), region.end())

    @classmethod
    def TupleToRegion(cls, tpl):
        return sublime.Region(tpl[0], tpl[1])

    @classmethod
    def RegionToTextInView(cls, view):
        def fn(region): return view.substr(region)
        return fn

    @classmethod
    def FilterDuplicateRegions(cls, _list_regions):
        list_regions = list(set(map(Bryn.RegionToTuple, _list_regions)))
        list_regions =     list(map(Bryn.TupleToRegion, list_regions))
        return list_regions

    @classmethod
    def ZoomToRegionInView(cls, region, view):
        view.show_at_center(region)
        view.sel().clear()
        view.sel().add(region)

    @classmethod
    def map_funcs(cls, obj, func_list):
        def recursiv(_obj, fl):
            if len(fl) > 0:
                func = fl[0]
                fl_tail = list(fl)
                fl_tail.remove(func)
                return recursiv(func(_obj), fl_tail)
            else:
                return _obj
        return recursiv(obj, func_list)





