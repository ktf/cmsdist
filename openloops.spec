### RPM external openloops 1.0.1
%define tag 3c7d667df8681acd8487f5326cdaefdf8832af3e
%define branch cms/v%{realversion}
%define github_user cms-externals
Source: git+https://github.com/%github_user/root.git?obj=%{branch}/%{tag}&export=%{n}-%{realversion}&output=/%{n}-%{realversion}-%{tag}.tgz

BuildRequires: python

%define keep_archives true

%prep
%setup -n %{n}-%{realversion}

%build
./scons
%install
