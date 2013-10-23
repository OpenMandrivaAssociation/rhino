# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define cvs_version 1_7R1
%define archive_version 1_7R1
%define section     free
%define gcj_support 0

Name:           rhino
Version:        1.7
Release:        12
Epoch:          0
Summary:        JavaScript for Java
License:        MPL
Source0:        ftp://ftp.mozilla.org/pub/mozilla.org/js/rhino%{archive_version}.zip
Source1:        http://java.sun.com/products/jfc/tsc/articles/treetable2/downloads/src.zip
Source2:        %{name}.script
Patch0:                http://svn.dojotoolkit.org/dojo/trunk/buildscripts/lib/custom_rhino.diff
Patch1:                rhino-no-xmlbeans.patch
URL:            http://www.mozilla.org/rhino/
Group:          Development/Java
#Requires:       xmlbeans
BuildRequires:  java-rpmbuild
BuildRequires:  ant
#BuildRequires:  xmlbeans
%if %{gcj_support}
BuildRequires:   java-gcj-compat-devel
%else
BuildArch:       noarch
BuildRequires:   java-devel >= 0:1.4.2 
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Rhino is an open-source implementation of JavaScript written entirely
in Java. It is typically embedded into Java applications to provide
scripting to end users.

This version contains Dojo's JavaScript compression patch.

This version does not contain E4X due to missing xmlbeans/xbean.jar.

%package        demo
Summary:        Examples for %{name}
Group:          Development/Java

%description    demo
Examples for %{name}.

%package        manual

Summary:        Manual for %{name}
Group:          Development/Java

%description    manual
Documentation for %{name}.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description    javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{name}%{cvs_version}
%patch0 -p1
%patch1 -p1

# Fix build
%{__perl} -pi -e 's|.*<get.*src=.*>\n||' build.xml testsrc/build.xml toolsrc/org/mozilla/javascript/tools/debugger/build.xml xmlimplsrc/build.xml
%{__install} -D -p -m 644 %{SOURCE1} toolsrc/org/mozilla/javascript/tools/debugger/downloaded/swingExSrc.zip

# Fix manifest
%{__perl} -pi -e 's|^Class-Path:.*\n||g' src/manifest

# Add jpp release info to version
%{__perl} -pi -e 's|^implementation.version: Rhino .* release .* \${implementation.date}|implementation.version: Rhino %{version} release %{release} \${implementation.date}|' build.properties

%build
export CLASSPATH=
export OPT_JAR_LIST=:
#%%{ant} -Dxbean.jar=$(build-classpath xmlbeans/xbean) jar javadoc
%{ant} -Dxbean.jar= -Djsr173.jar= -Dxmlimplsrc-build-file= jar javadoc

pushd examples
export CLASSPATH=../build/%{name}%{cvs_version}/js.jar:$(build-classpath xmlbeans/xbean 2>/dev/null)
%{javac} *.java
%{jar} cvf ../build/%{name}%{cvs_version}/%{name}-examples-%{version}.jar *.class
popd

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}
cp -a build/%{name}%{cvs_version}/js.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
cp -a build/%{name}%{cvs_version}/%{name}-examples-%{version}.jar %{buildroot}%{_javadir}/%{name}-examples-%{version}.jar
(cd %{buildroot}%{_javadir} && %{__ln_s} %{name}-%{version}.jar js-%{version}.jar)
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `echo $jar| %{__sed} "s|-%{version}||g"`; done)

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -a build/%{name}%{cvs_version}/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}
%{_bindir}/find %{buildroot}%{_javadocdir}/%{name}-%{version} -type f -name '*.html' | %{_bindir}/xargs %{__perl} -pi -e 's/\r$//g'

# script
%{__mkdir_p} %{buildroot}%{_bindir}
%{__install} -m 755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}

# examples
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}
cp -a examples/* %{buildroot}%{_datadir}/%{name}

# aot compile
%{gcj_compile}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/%{name}
%{_javadir}/*.jar
%{gcj_files}

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%if 0
%doc build/%{name}%{cvs_version}/docs/*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}


%changelog
* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 0:1.7-0.0.7mdv2011.0
+ Revision: 669424
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.7-0.0.6mdv2011.0
+ Revision: 607365
- rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0:1.7-0.0.5mdv2010.1
+ Revision: 523921
- rebuilt for 2010.1

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 0:1.7-0.0.4mdv2010.0
+ Revision: 426914
- rebuild

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 0:1.7-0.0.3mdv2009.1
+ Revision: 351560
- rebuild

* Wed Jun 18 2008 Alexander Kurtakov <akurtakov@mandriva.org> 0:1.7-0.0.2mdv2009.0
+ Revision: 225399
- switch to the 1.7 release, disable gcj_compile

* Sat Jan 12 2008 David Walluck <walluck@mandriva.org> 0:1.7-0.0.1mdv2008.1
+ Revision: 149258
- 1_7R1-RC1

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Dec 16 2007 Anssi Hannula <anssi@mandriva.org> 0:1.6-0.r5.5mdv2008.1
+ Revision: 120815
- buildrequires java-rpmbuild

* Sat Sep 15 2007 Anssi Hannula <anssi@mandriva.org> 0:1.6-0.r5.4mdv2008.0
+ Revision: 87352
- rebuild to filter out autorequires of GCJ AOT objects
- remove unnecessary Requires(post) on java-gcj-compat

* Sat Sep 08 2007 Pascal Terjan <pterjan@mandriva.org> 0:1.6-0.r5.3mdv2008.0
+ Revision: 82690
- update to new version


* Mon Mar 12 2007 David Walluck <walluck@mandriva.org> 0:1.6-0.r5.2mdv2007.1
+ Revision: 141810
- fix gcj_support
- spec cleanup

* Mon Dec 11 2006 David Walluck <walluck@mandriva.org> 0:1.6-0.r5.1mdv2007.1
+ Revision: 95055
- 1.6.0R5
  fix eol for javadoc
- Import rhino

* Thu Jun 15 2006 David Walluck <walluck@mandriva.org> 0:1.6-0.r2.2.1mdv2007.0
- bunmp release
- still no E4X implementation (xmlbeans) or bea-stax-api

* Fri Jun 02 2006 David Walluck <walluck@mandriva.org> 0:1.6-0.r2.1.1mdv2007.0
- release

* Thu Jun 01 2006 Fernando Nasser <fnasser@redhat.com> 0:1.6-0.r2.1jpp
- Upgrade to RC2

* Tue Apr 25 2006 Fernando Nasser <fnasser@redhat.com> 0:1.6-0.r1.2jpp
- First JPP 1.7 build

* Thu Dec 02 2004 David Walluck <david@jpackage.org> 0:1.6-0.r1.1jpp
- 1_6R1
- add demo subpackage containing example code
- add jpp release info to implementation version
- add script to launch js shell
- build E4X implementation (Requires: xmlbeans)
- remove `Class-Path' from manifest

* Wed Aug 25 2004 Fernando Nasser <fnasser@redhat.com> - 0:1.5-1.R5.1jpp
- Update to 1.5R5.
- Rebuild with Ant 1.6.2

