package com.example.service;

import java.util.List;
import java.util.Optional;
import com.example.model.User;
import com.example.exception.UserNotFoundException;

/**
 * 用户服务类
 * @author 张三
 * @version 2.0
 */
public class UserService {
    
    private UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    /**
     * 获取所有用户
     * @return 用户列表
     */
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    /**
     * 根据ID获取用户
     * @param id 用户ID
     * @return 用户对象
     * @throws UserNotFoundException 用户不存在时抛出
     */
    public User getUserById(Long id) throws UserNotFoundException {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("用户不存在: " + id));
    }
    
    /**
     * 更新用户信息（带参数校验）
     * @param user 用户对象
     */
    public void updateUser(User user) {
        if (user == null || user.getId() == null) {
            throw new IllegalArgumentException("用户信息不能为空");
        }
        userRepository.save(user);
    }
    
    /**
     * 删除用户
     * @param id 用户ID
     */
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}
