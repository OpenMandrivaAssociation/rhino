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
%define archive_version 1_7R1-RC1
%define section     free
%define gcj_support 1

Name:           rhino
Version:        1.7
Release:        %mkrel 0.0.1
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
#Vendor:         JPackage Project
#Distribution:   JPackage
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
%{__cp} -a build/%{name}%{cvs_version}/js.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
%{__cp} -a build/%{name}%{cvs_version}/%{name}-examples-%{version}.jar %{buildroot}%{_javadir}/%{name}-examples-%{version}.jar
(cd %{buildroot}%{_javadir} && %{__ln_s} %{name}-%{version}.jar js-%{version}.jar)
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s} ${jar} `echo $jar| %{__sed} "s|-%{version}||g"`; done)

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a build/%{name}%{cvs_version}/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}
%{_bindir}/find %{buildroot}%{_javadocdir}/%{name}-%{version} -type f -name '*.html' | %{_bindir}/xargs %{__perl} -pi -e 's/\r$//g'

# script
%{__mkdir_p} %{buildroot}%{_bindir}
%{__install} -m 755 %{SOURCE2} %{buildroot}%{_bindir}/%{name}

# examples
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}
%{__cp} -a examples/* %{buildroot}%{_datadir}/%{name}

# aot compile
%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

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
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

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
