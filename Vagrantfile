# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure(2) do |node|
  node.vm.box              = "landregistry/centos"
  node.vm.box_version      = "0.3"
  node.vm.box_check_update = true
  node.ssh.forward_agent = true

  # Prevent annoying "stdin: is not a tty" errors from displaying during 'vagrant up'
  node.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  # Run script to configure environment
  node.vm.provision :shell, :inline => "source /vagrant/local/setup-environment"

  node.vm.provider :virtualbox do |vb|
    vb.customize ['modifyvm', :id, '--memory', ENV['VM_MEMORY'] || 4096]
    vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
    vb.customize ['modifyvm', :id, '--natdnsproxy1', 'on']
    vb.customize ["modifyvm", :id, "--cpus", ENV['VM_CPUS'] || 4]
  end
end
