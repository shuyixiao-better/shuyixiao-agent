package com.example.service;

import java.util.List;
import com.example.model.User;

/**
 * 用户服务类
 */
public class UserService {
    
    private UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    /**
     * 获取所有用户
     */
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    /**
     * 根据ID获取用户
     */
    public User getUserById(Long id) {
        return userRepository.findById(id).orElse(null);
    }
    
    /**
     * 更新用户信息
     */
    public void updateUser(User user) {
        userRepository.save(user);
    }
}
